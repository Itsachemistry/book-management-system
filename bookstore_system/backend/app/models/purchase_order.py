from datetime import datetime, timezone # 导入 timezone
from ..database import db

# 订单状态常量
ORDER_STATUS = {
    'UNPAID': 'UNPAID',        # 未支付
    'PAID': 'PAID',            # 已支付
    'RETURNED': 'RETURNED',    # 已退货
    'STOCKED': 'STOCKED'       # 已入库
}


class PurchaseOrder(db.Model):
    """进货订单主表"""
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = db.Column(db.String(20), default=ORDER_STATUS['UNPAID'], nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), default=0.0, nullable=False)
    supplier = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    
    # 关联创建订单的用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('purchase_orders', lazy=True))
    
    # 关联订单项
    items = db.relationship('PurchaseOrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'
    
    def calculate_total(self):
        """计算订单总金额"""
        self.total_amount = sum(item.subtotal for item in self.items)
        return self.total_amount


class PurchaseOrderItem(db.Model):
    """进货订单项表"""
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    
    # 书籍信息 - 可以是现有书籍，也可以是新书
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    # 如果是新书，记录新书的信息
    isbn = db.Column(db.String(20))
    title = db.Column(db.String(200))
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    
    # 进货信息
    quantity = db.Column(db.Integer, nullable=False, default=1)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    suggested_retail_price = db.Column(db.Numeric(10, 2))  # 建议零售价
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关联的书籍 (可能为空，如果是新书)
    book = db.relationship('Book', backref=db.backref('purchase_items', lazy=True))
    
    @property
    def subtotal(self):
        """计算小计金额"""
        return self.purchase_price * self.quantity
    
    def __repr__(self):
        book_info = self.title if not self.book_id else self.book.name
        return f'<OrderItem {book_info} x {self.quantity}>'

