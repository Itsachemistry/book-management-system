from ..database import db
from datetime import datetime, timezone, timedelta  # 添加 timedelta 导入

# 定义中国标准时区 (UTC+8)
CST = timezone(timedelta(hours=8))

class Book(db.Model):
    """
    书籍模型，用于存储书店中的书籍信息
    """
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    publisher = db.Column(db.String(100))
    author = db.Column(db.String(100), index=True)
    retail_price = db.Column(db.Numeric(10, 2), nullable=False)  # 零售价格，使用Numeric确保精度
    quantity = db.Column(db.Integer, default=0, nullable=False)  # 库存数量
    is_active = db.Column(db.Boolean, default=True)  # 用于逻辑删除
    # 使用 CST 时区创建时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(CST))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(CST), 
                          onupdate=lambda: datetime.now(CST))  # 直接存储中国标准时间
    
    def __repr__(self):
        return f"<Book {self.name} (ISBN: {self.isbn})>"
    
    def to_dict(self):
        """将书籍转换成字典便于API返回"""
        # 直接使用存储的时间，不需要进行时区转换
        return {
            'id': self.id,
            'isbn': self.isbn,
            'name': self.name,
            'publisher': self.publisher,
            'author': self.author,
            'retail_price': float(self.retail_price),
            'quantity': self.quantity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def decrease_stock(self, amount):
        """减少库存
        
        Args:
            amount: 要减少的数量
            
        Returns:
            bool: 库存是否足够
        """
        if self.quantity < amount:
            return False
        
        self.quantity -= amount
        return True
        
    def increase_stock(self, amount, suggested_retail_price=None):
        """增加库存
        
        Args:
            amount: 要增加的数量
            suggested_retail_price: 可选的新零售价
        """
        # 使用字典更新方式，强制SQLAlchemy标记为脏
        update_dict = {'quantity': self.quantity + amount}
        
        # 如果提供了零售价，添加到更新字典
        if suggested_retail_price is not None:
            update_dict['retail_price'] = suggested_retail_price
        
        # 使用SQLAlchemy的update方法更新
        for key, value in update_dict.items():
            setattr(self, key, value)
         
        # 显式更新updated_at字段（使用 CST 时间）
        self.updated_at = datetime.now(CST)
        
        # 确保SQLAlchemy识别到对象已被修改
        db.session.add(self)
        
        return self  # 返回自身方便链式调用

def update_stock_from_order(order):
    """根据订单更新库存
    
    Args:
        order: 包含订单项的订单对象
    """
    for item in order.items:
        if item.book_id:
            book = Book.query.get(item.book_id)
            if book:
                # 这里直接调用 increase_stock，但没有传递 suggested_retail_price
                book.increase_stock(item.quantity)
                
                # 确保明确更新时间戳
                book.updated_at = datetime.now(CST)
                db.session.add(book)

