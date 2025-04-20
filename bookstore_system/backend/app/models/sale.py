from datetime import datetime, timezone  # 导入 timezone
from ..database import db
from decimal import Decimal

# 销售订单状态常量
SALE_STATUS = {
    'COMPLETED': 'COMPLETED',    # 已完成
    'REFUNDED': 'REFUNDED',      # 已退款
    'CANCELLED': 'CANCELLED'     # 已取消
}


class Sale(db.Model):
    """销售订单主表"""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(50), unique=True, nullable=False)
    sale_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  # 使用 timezone.utc
    status = db.Column(db.String(20), default=SALE_STATUS['COMPLETED'], nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), default=0.0, nullable=False)
    customer_name = db.Column(db.String(100))  # 可选的客户信息
    remarks = db.Column(db.Text)
    
    # 关联创建销售的用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('sales', lazy=True))
    
    # 关联销售项
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 使用 timezone.utc
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 使用 timezone.utc
    
    def __repr__(self):
        return f'<Sale {self.sale_number}>'
    
    def calculate_total(self):
        """计算订单总金额"""
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount


class SaleItem(db.Model):
    """销售订单项表"""
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    
    # 书籍信息
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('sale_items', lazy=True))
    
    # 销售信息
    quantity = db.Column(db.Integer, nullable=False, default=1)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)  # 实际销售单价
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 使用 timezone.utc
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 使用 timezone.utc
    
    @property
    def subtotal(self):
        """计算小计金额"""
        return self.sale_price * self.quantity
    
    def __repr__(self):
        return f'<SaleItem {self.book.name} x {self.quantity}>'

