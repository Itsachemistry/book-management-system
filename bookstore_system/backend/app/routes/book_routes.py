from flask import Blueprint, request, jsonify, g, abort
from werkzeug.exceptions import BadRequest
from ..models.book import Book
from ..schemas.book_schema import BookSchema, BookCreateSchema, BookUpdateSchema, BookQuerySchema
from ..utils.decorators import login_required, admin_required
from .. import db
from sqlalchemy import or_
from marshmallow import ValidationError

# 创建蓝图
book_bp = Blueprint('book', __name__, url_prefix='/api/books')

@book_bp.route('/', methods=['GET'])
def list_books():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    active_only = request.args.get('active_only', 'false').lower() == 'true'

    query = Book.query
    if search:
        query = query.filter(Book.name.ilike(f'%{search}%'))
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

