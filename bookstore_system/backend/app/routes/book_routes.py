from flask import Blueprint, request, jsonify, g, abort
from werkzeug.exceptions import BadRequest
from ..models.book import Book
from ..schemas.book_schema import BookSchema, BookCreateSchema, BookUpdateSchema, BookQuerySchema
from ..utils.decorators import login_required, admin_required
from .. import db
from sqlalchemy import or_
from marshmallow import ValidationError, Schema, fields
from ..models.purchase_order import PurchaseOrder, PurchaseOrderItem
import re

# 创建蓝图
book_bp = Blueprint('book', __name__, url_prefix='/api/books')

@book_bp.route('/', methods=['GET'])
def list_books():
    """
    获取书籍列表，支持搜索和分页
    ---
    参数:
      - search: 搜索关键词(可选，搜索书名、作者或ISBN)
      - page: 页码(可选，默认1)
      - per_page: 每页数量(可选，默认20)
      - active_only: 是否仅显示有效书籍(可选，默认True)
    权限: 任何用户
    返回:
      - 200: 返回书籍列表和分页信息
    """
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    active_only = request.args.get('active_only', 'false').lower() == 'true'

    query = Book.query
    
    # 改进搜索逻辑
    if search:
        # 检查是否是ISBN格式（纯数字或带连字符）
        is_isbn_like = bool(re.match(r'^[0-9\-]+$', search))
        
        if is_isbn_like:
            # ISBN搜索使用包含匹配，而不是前缀匹配
            query = query.filter(Book.isbn.like(f'%{search}%'))
        else:
            # 一般搜索 - 同时搜索书名、作者和ISBN
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Book.name.ilike(search_term),
                    Book.author.ilike(search_term),
                    Book.isbn.ilike(search_term)
                )
            )
            
    if active_only:
        query = query.filter(Book.is_active.is_(True))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    books = BookSchema(many=True).dump(pagination.items)

    return jsonify({
        'items': books,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    })

@book_bp.route('/<isbn_or_id>', methods=['GET'])
@login_required
def get_book(isbn_or_id):
    """
    获取单本书籍详情
    ---
    参数:
      - isbn_or_id: 书籍ID或ISBN
    权限: 任何登录用户
    返回:
      - 200: 返回书籍详情
      - 404: 书籍未找到
    """
    # 尝试通过ID或ISBN查找书籍
    book = None
    
    # 先尝试通过ID查找
    if isbn_or_id.isdigit():
        book = Book.query.get(int(isbn_or_id))
    
    # 如果没找到，通过ISBN查找
    if book is None:
        book = Book.query.filter_by(isbn=isbn_or_id).first()
    
    # 如果仍然没找到，返回404
    if book is None:
        abort(404, description="书籍未找到")
    
    return jsonify(BookSchema().dump(book))

@book_bp.route('/isbn/<isbn>', methods=['GET'])
@login_required
def get_book_by_isbn(isbn):
    """
    根据ISBN获取书籍信息
    ---
    参数:
      - isbn: 书籍ISBN
    权限: 任何登录用户
    返回:
      - 200: 返回书籍详情
      - 404: 书籍未找到
    """
    book = Book.query.filter_by(isbn=isbn).first()
    
    if book is None:
        abort(404, description="未找到匹配的ISBN图书")
    
    return jsonify(BookSchema().dump(book))

@book_bp.route('', methods=['POST'])
@admin_required
def create_book():
    # 1. JSON 解析校验
    try:
        payload = request.get_json()
    except BadRequest:
        return jsonify({"error": "请求体必须为 JSON 格式"}), 400
    if payload is None:
        return jsonify({"error": "请求体不能为空"}), 400

    # 2. 数据校验
    schema = BookCreateSchema()
    try:
        data = schema.load(payload)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    # 3. ISBN 唯一性检查
    existing = Book.query.filter_by(isbn=data['isbn']).first()
    if existing:
        return jsonify({"error": "具有相同 ISBN 的书籍已存在"}), 409

    # 4. 创建并保存
    book = Book(**data)
    db.session.add(book)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"保存书籍时发生错误: {str(e)}"}), 500

    return jsonify(BookSchema().dump(book)), 201

@book_bp.route('/<isbn_or_id>', methods=['PUT'])
@admin_required
def update_book(isbn_or_id):
    """
    更新书籍信息
    ---
    参数:
      - isbn_or_id: 书籍ID或ISBN
    请求体: BookUpdateSchema
    权限: 仅管理员
    返回:
      - 200: 更新成功，返回更新后的书籍详情
      - 400: 验证失败
      - 404: 书籍未找到
    """
    # 首先找到要更新的书籍
    book = None
    
    # 尝试通过ID查找
    if isbn_or_id.isdigit():
        book = Book.query.get(int(isbn_or_id))
    
    # 如果没找到，尝试通过ISBN查找
    if book is None:
        book = Book.query.filter_by(isbn=isbn_or_id).first()
    
    # 如果仍然没找到，返回404
    if book is None:
        abort(404, description="要更新的书籍未找到")
    
    # 验证并加载更新数据
    schema = BookUpdateSchema()
    try:
        # 使用 request.get_json() 获取原始 JSON 数据
        json_data = request.get_json()
        if not json_data:
             return jsonify({"error": "请求体不能为空或非 JSON 格式"}), 400
        data = schema.load(json_data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e: # 捕获可能的 JSON 解析错误
        return jsonify({"error": f"解析请求数据时出错: {str(e)}"}), 400

    # 恢复 ISBN 唯一性检查逻辑
    # 如果请求中包含 'isbn' 并且它与当前书籍的 ISBN 不同
    if 'isbn' in data and data['isbn'] != book.isbn:
        # 检查新的 ISBN 是否已被其他书籍使用
        existing_book = Book.query.filter(Book.isbn == data['isbn'], Book.id != book.id).first()
        if existing_book:
            return jsonify({"error": {"isbn": ["具有相同ISBN的其他书籍已存在"]}}), 409 # 返回更符合 Marshmallow 错误格式的响应
    
    # 更新书籍属性
    for key, value in data.items():
        setattr(book, key, value)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # 记录更详细的错误日志会更好
        print(f"Error updating book: {str(e)}") # 临时打印，建议使用日志库
        return jsonify({"error": f"更新书籍时发生数据库错误"}), 500 # 隐藏具体错误细节
    
    return jsonify(BookSchema().dump(book))

@book_bp.route('/<isbn_or_id>', methods=['DELETE'])
@admin_required
def delete_book(isbn_or_id):
    """
    删除书籍 (物理删除)
    ---
    参数:
      - isbn_or_id: 书籍ID或ISBN
    权限: 仅管理员
    返回:
      - 200: 删除成功
      - 404: 书籍未找到
    注意: 这是物理删除，将从数据库中永久移除记录
    """
    # 首先找到要删除的书籍
    book = None
    
    # 尝试通过ID查找
    if isbn_or_id.isdigit():
        book = Book.query.get(int(isbn_or_id))
    
    # 如果没找到，尝试通过ISBN查找
    if book is None:
        book = Book.query.filter_by(isbn=isbn_or_id).first()
    
    # 如果仍然没找到，返回404
    if book is None:
        abort(404, description="要删除的书籍未找到")
    
    # 执行物理删除
    db.session.delete(book)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # 建议使用日志记录错误
        print(f"Error deleting book: {str(e)}") 
        return jsonify({"error": f"删除书籍时发生数据库错误"}), 500
    
    return jsonify({"message": "书籍已成功删除"})

@book_bp.route('/isbn-references/<isbn>', methods=['GET'])
@admin_required
def get_isbn_references(isbn):
    """
    查询指定ISBN在各个表中的引用
    ---
    参数:
      - isbn: 书籍ISBN号
    权限: 仅管理员
    返回:
      - 200: 返回所有引用信息
      - 404: 书籍未找到
    """
    # 查找书籍基本信息
    book = Book.query.filter_by(isbn=isbn).first()
    
    if not book:
        return jsonify({"error": f"未找到ISBN为 {isbn} 的书籍"}), 404
    
    result = {
        "book": BookSchema().dump(book),
        "purchase_items": [],
        "purchase_orders": []
    }
    
    # 查找直接通过ISBN记录的采购项
    direct_purchase_items = PurchaseOrderItem.query.filter_by(isbn=isbn).all()
    
    # 查找通过book_id关联的采购项
    book_id_purchase_items = PurchaseOrderItem.query.filter_by(book_id=book.id).all()
    
    # 合并两种查询结果(去重)
    all_item_ids = set()
    all_purchase_items = []
    
    for item in direct_purchase_items + book_id_purchase_items:
        if item.id not in all_item_ids:
            all_purchase_items.append(item)
            all_item_ids.add(item.id)
    
    # 查找关联的订单
    if all_purchase_items:
        # 准备schema
        class SimplePurchaseItemSchema(Schema):
            id = fields.Integer()
            purchase_order_id = fields.Integer()
            quantity = fields.Integer()
            purchase_price = fields.Decimal(as_string=True)
            title = fields.String()
            author = fields.String()
            publisher = fields.String()
            order_date = fields.DateTime(attribute="order.order_date")
            order_status = fields.String(attribute="order.status")
            order_number = fields.String(attribute="order.order_number")
            supplier = fields.String(attribute="order.supplier")
        
        # 序列化采购项
        purchase_item_schema = SimplePurchaseItemSchema(many=True)
        result["purchase_items"] = purchase_item_schema.dump(all_purchase_items)
        
        # 获取相关的采购订单ID
        order_ids = list(set(item.purchase_order_id for item in all_purchase_items))
        orders = PurchaseOrder.query.filter(PurchaseOrder.id.in_(order_ids)).all()
        
        class SimplePurchaseOrderSchema(Schema):
            id = fields.Integer()
            order_number = fields.String()
            order_date = fields.DateTime()
            status = fields.String()
            supplier = fields.String()
            total_amount = fields.Decimal(as_string=True)
        
        order_schema = SimplePurchaseOrderSchema(many=True)
        result["purchase_orders"] = order_schema.dump(orders)
    
    # 返回结果
    return jsonify(result)

