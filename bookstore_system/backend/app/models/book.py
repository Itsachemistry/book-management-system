from ..database import db
from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Book {self.name} (ISBN: {self.isbn})>"
    
    def to_dict(self):
        """将书籍转换成字典便于API返回"""
        return {
            'id': self.id,
            'isbn': self.isbn,
            'name': self.name,
            'publisher': self.publisher,
            'author': self.author,
            'retail_price': float(self.retail_price),  # 将Decimal转为float便于JSON序列化
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
        
    def increase_stock(self, amount):
        """增加库存
        
        Args:
            amount: 要增加的数量
        """
        self.quantity += amount

