from flask import Blueprint, request, jsonify, g, abort
from ..models.purchase_order import PurchaseOrder, PurchaseOrderItem, ORDER_STATUS
from ..models.book import Book
from ..models.transaction import Transaction, TRANSACTION_TYPES
from ..schemas.purchase_order_schema import (
    PurchaseOrderSchema, PurchaseOrderCreateSchema, PurchaseOrderUpdateSchema, PurchaseOrderQuerySchema
)
from ..utils.decorators import login_required, admin_required
from .. import db
from sqlalchemy import and_, or_
import uuid
from datetime import datetime

# 创建蓝图
procurement_bp = Blueprint('procurement', __name__)

@procurement_bp.route('/orders', methods=['POST'])
@admin_required
def create_order():
    """
    创建新的进货订单
    ---
    权限: 仅管理员
    """
    schema = PurchaseOrderCreateSchema()
    data = schema.load(request.json)
    
    # 创建订单
    order = PurchaseOrder(
        order_number=f"PO-{uuid.uuid4().hex[:8].upper()}",
        user_id=g.user.id,
        supplier=data.get('supplier'),
        remarks=data.get('remarks')
    )
    
    # 添加订单项
    for item_data in data['items']:
        order_item = PurchaseOrderItem(
            book_id=item_data.get('book_id'),
            isbn=item_data.get('isbn'),
            title=item_data.get('title'),
            author=item_data.get('author'),
            publisher=item_data.get('publisher'),
            quantity=item_data['quantity'],
            purchase_price=item_data['purchase_price'],
            suggested_retail_price=item_data.get('suggested_retail_price')
        )
        order.items.append(order_item)
    
    # 计算订单总金额
    order.calculate_total()
    
    # 保存到数据库
    db.session.add(order)
    db.session.commit()
    
    # 返回创建的订单
    return jsonify(PurchaseOrderSchema().dump(order)), 201


@procurement_bp.route('/orders', methods=['GET'])
@admin_required
def get_orders():
    """
    获取进货订单列表
    ---
    权限: 仅管理员
    查询参数:
      status: 订单状态过滤
      start_date: 开始日期过滤
      end_date: 结束日期过滤
      page: 页码
      per_page: 每页条数
    """
    # 验证和提取查询参数
    schema = PurchaseOrderQuerySchema()
    params = schema.load(request.args)
    
    # 构建查询
    query = PurchaseOrder.query
    
    # 应用过滤条件
    if 'status' in params and params['status']:
        query = query.filter(PurchaseOrder.status == params['status'])
        
    if 'start_date' in params and params['start_date']:
        query = query.filter(PurchaseOrder.order_date >= params['start_date'])
        
    if 'end_date' in params and params['end_date']:
        # 如果是日期，则需要设置为当天结束时间
        end_datetime = datetime.combine(params['end_date'], datetime.max.time())
        query = query.filter(PurchaseOrder.order_date <= end_datetime)
    
    # 分页
    page = params.get('page', 1)
    per_page = params.get('per_page', 20)
    
    # 排序 - 最新的订单排在前面
    query = query.order_by(PurchaseOrder.created_at.desc())
    
    # 执行分页查询
    paginated_orders = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 准备返回数据
    result = {
        'orders': PurchaseOrderSchema(many=True).dump(paginated_orders.items),
        'pagination': {
            'page': paginated_orders.page,
            'per_page': paginated_orders.per_page,
            'total': paginated_orders.total,
            'pages': paginated_orders.pages
        }
    }
    
    return jsonify(result)


@procurement_bp.route('/orders/<int:order_id>', methods=['GET'])
@admin_required
def get_order(order_id):
    """
    获取单个进货订单的详细信息
    ---
    权限: 仅管理员
    """
    order = PurchaseOrder.query.get_or_404(order_id)
    return jsonify(PurchaseOrderSchema().dump(order))


@procurement_bp.route('/orders/<int:order_id>', methods=['PUT'])
@admin_required
def update_order(order_id):
    """
    更新进货订单基本信息
    ---
    权限: 仅管理员
    注意: 此端点仅允许更新不影响订单状态的信息，如供应商和备注
    """
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # 检查订单状态 - 只允许修改未支付的订单
    if order.status != ORDER_STATUS['UNPAID']:
        abort(400, description="只能修改未支付的订单")
    
    schema = PurchaseOrderUpdateSchema()
    data = schema.load(request.json)
    
    # 更新允许修改的字段
    if 'supplier' in data:
        order.supplier = data['supplier']
    if 'remarks' in data:
        order.remarks = data['remarks']
    
    db.session.commit()
    
    return jsonify(PurchaseOrderSchema().dump(order))


@procurement_bp.route('/orders/<int:order_id>/pay', methods=['POST'])
@admin_required
def pay_order(order_id):
    """
    支付进货订单
    ---
    权限: 仅管理员
    行为: 更新订单状态为已支付，创建支出类型的财务记录
    """
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # 检查订单状态
    if order.status != ORDER_STATUS['UNPAID']:
        abort(400, description="只有未支付的订单可以进行支付操作")
    
    # 更新订单状态
    order.status = ORDER_STATUS['PAID']
    
    # 创建财务记录
    transaction = Transaction(
        transaction_type=TRANSACTION_TYPES['EXPENSE'],
        amount=order.total_amount,
        description=f"支付进货订单 {order.order_number}",
        user_id=g.user.id,
        reference_id=order.id,
        reference_type='purchase_order'
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': '订单支付成功',
        'order': PurchaseOrderSchema().dump(order)
    })


@procurement_bp.route('/orders/<int:order_id>/return', methods=['POST'])
@admin_required
def return_order(order_id):
    """
    退货订单
    ---
    权限: 仅管理员
    行为: 仅当状态为"未支付"时，将订单状态更新为"已退货"
    """
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # 检查订单状态
    if order.status != ORDER_STATUS['UNPAID']:
        abort(400, description="只有未支付的订单可以进行退货操作")
    
    # 更新订单状态
    order.status = ORDER_STATUS['RETURNED']
    
    db.session.commit()
    
    return jsonify({
        'message': '订单已标记为退货',
        'order': PurchaseOrderSchema().dump(order)
    })


@procurement_bp.route('/orders/<int:order_id>/stock-in', methods=['POST'])
@admin_required
def stock_in(order_id):
    """
    图书入库
    ---
    权限: 仅管理员
    行为: 仅当状态为"已支付"时执行，增加/更新相关书籍的库存数量
    """
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # 检查订单状态
    if order.status != ORDER_STATUS['PAID']:
        abort(400, description="只有已支付的订单可以进行入库操作")
    
    # 处理每个订单项
    for item in order.items:
        # 如果关联到现有书籍
        if item.book_id:
            book = Book.query.get(item.book_id)
            if book:
                # 增加库存
                book.quantity += item.quantity
                # 更新零售价（如果提供了）
                if item.suggested_retail_price:
                    book.retail_price = item.suggested_retail_price
        else:
            # 创建新书
            book = Book(
                isbn=item.isbn,
                name=item.title,
                author=item.author,
                publisher=item.publisher,
                retail_price=item.suggested_retail_price or item.purchase_price * 1.5,  # 默认零售价是成本的1.5倍
                quantity=item.quantity,
                is_active=True
            )
            db.session.add(book)
            
            # 关联新书到订单项
            item.book_id = book.id
    
    # 更新订单状态
    order.status = ORDER_STATUS['STOCKED']
    
    db.session.commit()
    
    return jsonify({
        'message': '图书已成功入库',
        'order': PurchaseOrderSchema().dump(order)
    })

