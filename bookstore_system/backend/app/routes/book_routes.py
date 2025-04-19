from flask import Blueprint, request, jsonify, g, abort
from ..models.book import Book
from ..schemas.book_schema import BookSchema, BookCreateSchema, BookUpdateSchema
from ..utils.decorators import login_required, admin_required
from .. import db
from sqlalchemy import or_

# 创建蓝图
book_bp = Blueprint('books', __name__)

@book_bp.route('/', methods=['GET'])
@login_required
def get_books():
    """
    获取所有书籍的列表API
    
    支持查询参数:
    - search: 按书名、作者、ISBN搜索
    - page: 页码
    - per_page: 每页书籍数量
    - active_only: 是否只返回有效(非逻辑删除)的书籍
    
    返回:
    {
        "books": [书籍列表],
        "pagination": {
            "page": 当前页码,
            "per_page": 每页数量,
            "total": 总数,
            "pages": 总页数
        }
    }
    """
    # 获取查询参数
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    # 构建查询
    query = Book.query
    
    # 是否只查询有效书籍
    if active_only:
        query = query.filter_by(is_active=True)
    
    # 搜索功能
    if search:
        query = query.filter(
            or_(
                Book.name.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )
    
    # 分页查询
    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books = pagination.items
    
    # 序列化
    book_schema = BookSchema(many=True)
    book_data = book_schema.dump(books)
    
    return jsonify({
        'books': book_data,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })

@book_bp.route('/<isbn_or_id>', methods=['GET'])
@login_required
def get_book(isbn_or_id):
    """
    获取单本书籍详情API
    
    参数:
    - isbn_or_id: 书籍的ISBN或ID
    
    返回:
    {书籍详情}
    """
    # 尝试通过ID查找
    try:
        if isbn_or_id.isdigit():
            book = Book.query.get_or_404(int(isbn_or_id))
        else:
            book = Book.query.filter_by(isbn=isbn_or_id).first_or_404()
    except:
        abort(404, description="书籍不存在")
    
    # 序列化
    book_schema = BookSchema()
    book_data = book_schema.dump(book)
    
    return jsonify(book_data)

@book_bp.route('/', methods=['POST'])
@admin_required  # 只有管理员可以添加书籍
def create_book():
    """
    创建新书籍API
    
    请求体:
    {
        "isbn": "书籍ISBN",
        "name": "书籍名称",
        "publisher": "出版商(可选)",
        "author": "作者(可选)",
        "retail_price": 零售价格,
        "quantity": 初始库存数量
    }
    
    返回:
    {新创建的书籍详情}
    """
    # 反序列化并验证请求数据
    schema = BookCreateSchema()
    data = schema.load(request.get_json())
    
    # 创建新书籍
    book = Book(
        isbn=data['isbn'],
        name=data['name'],
        publisher=data.get('publisher'),
        author=data.get('author'),
        retail_price=data['retail_price'],
        quantity=data.get('quantity', 0)
    )
    
    # 保存到数据库
    db.session.add(book)
    db.session.commit()
    
    # 返回创建的书籍
    book_schema = BookSchema()
    return jsonify(book_schema.dump(book)), 201

@book_bp.route('/<int:book_id>', methods=['PUT'])
@admin_required  # 只有管理员可以更新书籍
def update_book(book_id):
    """
    更新书籍信息API
    
    参数:
    - book_id: 书籍ID
    
    请求体:
    {
        "name": "书籍名称(可选)",
        "publisher": "出版商(可选)",
        "author": "作者(可选)",
        "retail_price": 零售价格(可选),
        "quantity": 库存数量(可选),
        "is_active": 是否有效(可选)
    }
    
    返回:
    {更新后的书籍详情}
    """
    # 获取书籍
    book = Book.query.get_or_404(book_id)
    
    # 反序列化并验证请求数据
    schema = BookUpdateSchema()
    data = schema.load(request.get_json())
    
    # 更新字段
    for field, value in data.items():
        setattr(book, field, value)
    
    # 保存到数据库
    db.session.commit()
    
    # 返回更新后的书籍
    book_schema = BookSchema()
    return jsonify(book_schema.dump(book))

@book_bp.route('/<int:book_id>', methods=['DELETE'])
@admin_required  # 只有管理员可以删除书籍
def delete_book(book_id):
    """
    删除书籍API（逻辑删除）
    
    参数:
    - book_id: 书籍ID
    
    返回:
    { "message": "书籍已删除" }
    """
    # 获取书籍
    book = Book.query.get_or_404(book_id)
    
    # 执行逻辑删除（将is_active设为False）
    book.is_active = False
    db.session.commit()
    
    return jsonify({"message": "书籍已删除"})

# 注意: 完成此文件后，需要在app/__init__.py中注册这个Blueprint

