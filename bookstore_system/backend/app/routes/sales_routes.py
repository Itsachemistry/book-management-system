from flask import Blueprint, request, jsonify, g, abort, current_app
from ..models.sale import Sale, SaleItem, SALE_STATUS
from ..models.book import Book
from ..models.transaction import Transaction, TRANSACTION_TYPES
from ..schemas.sale_schema import (
    SaleSchema, SaleCreateSchema, SaleUpdateSchema, SaleQuerySchema
)
from ..utils.decorators import login_required, admin_required
from .. import db
from sqlalchemy import and_, or_
from datetime import datetime, timezone
from marshmallow import ValidationError, validates
import uuid

# 创建蓝图
sales_bp = Blueprint('sales', __name__)


@sales_bp.route('', methods=['POST'])
@login_required
def create_sale():
    """创建新的销售记录"""
    # 验证请求数据
    schema = SaleCreateSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        current_app.logger.info(f"销售验证失败: {err.messages}")
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating sale: {e}", exc_info=True)
        return jsonify({"error": "创建销售时发生内部错误"}), 500

    # 创建销售记录
    sale = Sale(
        sale_number=f"S-{uuid.uuid4().hex[:8].upper()}",
        user_id=g.user.id,
        customer_name=data.get('customer_name'),
        remarks=data.get('remarks')
    )

    # 添加销售项目并减少库存
    for item_data in data['items']:
        book = db.session.get(Book, item_data['book_id'])
        if not book:
            abort(400, description=f"Book with ID {item_data['book_id']} not found during processing.")

        # 刷新对象状态
        db.session.refresh(book)

        current_app.logger.debug(f"[create_sale] book {book.id} (refreshed) before sale qty={book.quantity}")

        # 库存检查
        if book.quantity < item_data['quantity']:
            current_app.logger.warning(f"Stock check failed for book {book.id}. Required: {item_data['quantity']}, Available: {book.quantity}")
            return jsonify({
                "error": {
                    "items": {
                        "message": f"书籍 '{book.name}' 库存不足，当前库存: {book.quantity}, 需要数量: {item_data['quantity']}"
                    }
                }
            }), 400

        # 减少库存
        if not book.decrease_stock(item_data['quantity']):
            return jsonify({
                "error": {
                    "items": {
                        "message": f"尝试减少书籍 '{book.name}' 库存时失败 (可能并发问题)"
                    }
                }
            }), 400

        db.session.add(book)

        sale_item = SaleItem(
            book_id=book.id,
            quantity=item_data['quantity'],
            sale_price=item_data['sale_price']
        )
        sale.items.append(sale_item)

    sale.calculate_total()

    db.session.add(sale)

    # 创建财务记录
    transaction = Transaction(
        transaction_type=TRANSACTION_TYPES['INCOME'],
        amount=sale.total_amount,
        transaction_date=datetime.now(timezone.utc),
        description=f"销售 {sale.sale_number}",
        reference_id=sale.id,
        reference_type='sale',
        user_id=g.user.id
    )
    db.session.add(transaction)

    try:
        db.session.commit()
        current_app.logger.info(f"Sale {sale.sale_number} created successfully. Book {book.id} quantity after commit: {book.quantity}")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error committing sale and transaction: {e}", exc_info=True)
        return jsonify({"error": "保存销售记录时发生数据库错误"}), 500

    return jsonify(SaleSchema().dump(sale)), 201


@sales_bp.route('', methods=['GET'])
@login_required
def get_sales():
    """
    获取销售记录列表
    ---
    权限: 任何登录用户
    """
    schema = SaleQuerySchema()
    try:
        params = schema.load(request.args)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    query = Sale.query

    if 'status' in params and params['status']:
        query = query.filter(Sale.status == params['status'])

    if 'start_date' in params and params['start_date']:
        start_datetime = datetime.combine(params['start_date'], datetime.min.time(), tzinfo=timezone.utc)
        query = query.filter(Sale.sale_date >= start_datetime)

    if 'end_date' in params and params['end_date']:
        end_datetime = datetime.combine(params['end_date'], datetime.max.time(), tzinfo=timezone.utc)
        query = query.filter(Sale.sale_date <= end_datetime)

    query = query.order_by(Sale.sale_date.desc())

    page = params.get('page', 1)
    per_page = params.get('per_page', 20)

    try:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        sales = pagination.items
    except Exception as e:
        current_app.logger.error(f"Error during sales pagination: {e}", exc_info=True)
        return jsonify({"error": "获取销售列表时出错"}), 500

    return jsonify({
        'sales': SaleSchema(many=True).dump(sales),
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }
    })


@sales_bp.route('/<int:sale_id>/refund', methods=['POST'])
@login_required
def refund_sale_route(sale_id):
    """对销售进行退款"""
    sale = db.session.get(Sale, sale_id)
    if not sale:
        abort(404, description="销售订单未找到")

    if g.user.id != sale.user_id and not (g.user.role in ['SUPER_ADMIN', 'ADMIN']):
        abort(403, description="无权执行此操作")

    if sale.status != SALE_STATUS['COMPLETED']:
        abort(400, description="只有已完成的订单才能退款")

    for item in sale.items:
        book = db.session.get(Book, item.book_id)
        if book:
            # 刷新对象状态
            db.session.refresh(book)
            current_app.logger.debug(f"[refund] book {book.id} (refreshed) before refund qty={book.quantity}")
            book.increase_stock(item.quantity)
            db.session.add(book)
            current_app.logger.debug(f"[refund] book {book.id} after increase_stock qty={book.quantity}")
        else:
            current_app.logger.warning(f"Book with ID {item.book_id} not found during refund for sale {sale_id}.")

    # 更新销售状态
    sale.status = SALE_STATUS['REFUNDED']
    sale.updated_at = datetime.now(timezone.utc)
    db.session.add(sale)

    # 添加退款记录
    transaction = Transaction(
        transaction_type=TRANSACTION_TYPES['REFUND'],
        amount=-sale.total_amount,
        transaction_date=datetime.now(timezone.utc),
        description=f"销售退款 {sale.sale_number}",
        reference_id=sale.id,
        reference_type='sale_refund',
        user_id=g.user.id
    )

    db.session.add(transaction)

    try:
        db.session.commit()
        current_app.logger.info(f"Sale {sale.sale_number} refunded successfully.")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error committing refund: {e}", exc_info=True)
        return jsonify({"error": "处理退款时发生数据库错误"}), 500

    return jsonify({
        "message": "退款处理成功",
        "sale": SaleSchema().dump(sale)
    })

