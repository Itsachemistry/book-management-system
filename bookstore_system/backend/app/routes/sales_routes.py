import uuid
from flask import Blueprint, request, jsonify, g, abort
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from .. import db
from ..models.sale import Sale, SaleItem, SALE_STATUS
from ..models.book import Book
from ..models.transaction import Transaction, TRANSACTION_TYPES
from ..schemas.sale_schema import SaleSchema, SaleCreateSchema, SaleUpdateSchema
from ..utils.decorators import login_required, admin_required

# 创建蓝图
sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')

@sales_bp.route('/', methods=['POST'])
@login_required
def create_sale():
    """
    创建新销售订单
    ---
    请求体: SaleCreateSchema
    权限: 任何用户
    返回:
      - 201: 创建成功，返回销售订单
      - 400: 请求数据验证失败
      - 409: 库存不足
    """
    try:
        payload = request.get_json()
    except BadRequest:
        return jsonify({"error": "请求体必须为JSON格式"}), 400
    
    if not payload:
        return jsonify({"error": "请求体不能为空"}), 400
    
    schema = SaleCreateSchema()
    try:
        data = schema.load(payload)
    except Exception as err:
        return jsonify({"error": err.messages}), 400
    
    # 生成销售单号
    sale_number = f"S{uuid.uuid4().hex[:8].upper()}"
    
    user_id = g.user.id if hasattr(g, 'user') and g.user else None
    
    sale = Sale(
        sale_number=sale_number,
        customer_name=data.get('customer_name'),
        contact=data.get('contact'),
        payment_method=data.get('payment_method', 'CASH'),
        remarks=data.get('remarks'),
        user_id=user_id,
        status=SALE_STATUS['COMPLETED']
    )
    
    db.session.add(sale)
    
    # 处理销售项并减少库存
    total_amount = 0
    for item_data in data['items']:
        book = Book.query.get(item_data['book_id'])
        if not book:
            db.session.rollback()
            return jsonify({"error": f"书籍ID {item_data['book_id']} 不存在"}), 404
        
        # 检查并减少库存
        try:
            book.decrease_stock(item_data['quantity'])
        except ValueError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 409
        
        # 创建销售项
        sale_item = SaleItem(
            sale=sale,
            book_id=book.id,
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(sale_item)
        total_amount += sale_item.subtotal
    
    # 设置订单总金额
    sale.total_amount = total_amount
    
    # 创建收入交易记录
    try:
        transaction = Transaction(
            amount=total_amount,
            type=TRANSACTION_TYPES['INCOME'],
            description=f"销售单 {sale_number}",
            reference_id=sale_number,
            user_id=user_id
        )
        db.session.add(transaction)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"创建财务记录失败: {str(e)}"}), 500
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"保存销售订单失败: {str(e)}"}), 500
    
    return jsonify(SaleSchema().dump(sale)), 201

@sales_bp.route('/', methods=['GET'])
@login_required
def list_sales():
    """
    获取销售订单列表
    ---
    查询参数:
      - page: 页码
      - per_page: 每页数量
      - status: 订单状态(可选)
      - start_date: 开始日期(可选)
      - end_date: 结束日期(可选)
    权限: 任何用户
    返回:
      - 200: 销售订单列表及分页信息
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Sale.query
    
    # 应用过滤条件
    if status:
        query = query.filter(Sale.status == status)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    if hasattr(g, 'user') and g.user and not g.user.is_admin():
        query = query.filter(Sale.user_id == g.user.id)
    
    # 按日期降序排列
    query = query.order_by(Sale.sale_date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    sales = pagination.items
    
    return jsonify({
        'items': SaleSchema(many=True).dump(sales),
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    })

@sales_bp.route('/<int:sale_id>', methods=['GET'])
@login_required
def get_sale(sale_id):
    """
    获取单个销售订单详情
    ---
    参数:
      - sale_id: 销售订单ID
    权限: 任何用户
    返回:
      - 200: 销售订单详情
      - 404: 订单不存在
    """
    sale = Sale.query.get_or_404(sale_id, description="销售订单不存在")
    
    return jsonify(SaleSchema().dump(sale))

@sales_bp.route('/<int:sale_id>/refund', methods=['POST'])
@login_required
def refund_sale(sale_id):
    """
    退款处理
    ---
    参数:
      - sale_id: 销售订单ID
    权限: 任何用户
    返回:
      - 200: 退款成功
      - 400: 订单状态不允许退款
      - 404: 订单不存在
    """
    sale = Sale.query.get_or_404(sale_id, description="销售订单不存在")
    
    # 检查订单状态是否允许退款
    if sale.status != SALE_STATUS['COMPLETED']:
        return jsonify({"error": "只有已完成的订单可以退款"}), 400
    
    # 更新订单状态
    sale.status = SALE_STATUS['REFUNDED']
    
    # 恢复库存
    for item in sale.items:
        book = item.book
        book.quantity += item.quantity
    
    user_id = g.user.id if hasattr(g, 'user') and g.user else None
    
    transaction = Transaction(
        amount=sale.total_amount,
        type=TRANSACTION_TYPES['EXPENSE'],
        description=f"销售单 {sale.sale_number} 退款",
        reference_id=sale.sale_number,
        user_id=user_id
    )
    db.session.add(transaction)
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"退款处理失败: {str(e)}"}), 500
    
    return jsonify({
        "message": "退款处理成功",
        "sale": SaleSchema().dump(sale)
    })

@sales_bp.route('/<int:sale_id>', methods=['DELETE'])
@login_required
def cancel_sale(sale_id):
    """
    取消销售订单
    ---
    参数:
      - sale_id: 销售订单ID
    权限: 任何用户
    返回:
      - 200: 取消成功
      - 400: 订单状态不允许取消
      - 404: 订单不存在
    """
    sale = Sale.query.get_or_404(sale_id, description="销售订单不存在")
    
    # 检查订单状态是否允许取消
    if sale.status != SALE_STATUS['COMPLETED']:
        return jsonify({"error": "只有已完成的订单可以取消"}), 400
    
    # 更新订单状态
    sale.status = SALE_STATUS['CANCELLED']
    
    # 恢复库存
    for item in sale.items:
        book = item.book
        book.quantity += item.quantity
    
    user_id = g.user.id if hasattr(g, 'user') and g.user else None
    
    transaction = Transaction(
        amount=sale.total_amount,
        type=TRANSACTION_TYPES['EXPENSE'],
        description=f"销售单 {sale.sale_number} 取消",
        reference_id=sale.sale_number,
        user_id=user_id
    )
    db.session.add(transaction)
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"取消订单失败: {str(e)}"}), 500
    
    return jsonify({
        "message": "销售订单已取消",
        "sale": SaleSchema().dump(sale)
    })

