from datetime import datetime
from ..database import db

# 交易类型常量
TRANSACTION_TYPES = {
    'INCOME': 'INCOME',      # 收入 (销售图书)
    'EXPENSE': 'EXPENSE',    # 支出 (采购图书)
    'REFUND': 'REFUND',      # 退款 (退货)
    'OTHER': 'OTHER'         # 其他
}

class Transaction(db.Model):
    """财务交易记录模型"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(200))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关联到操作用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    
    # 关联到相关单据 (可以是进货单或销售单)
    reference_id = db.Column(db.Integer)
    reference_type = db.Column(db.String(50))  # 'purchase_order' 或 'sale'
    
    # 审计字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.amount}>"

