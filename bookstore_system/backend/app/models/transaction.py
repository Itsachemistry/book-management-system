from datetime import datetime, timezone
from .. import db
from sqlalchemy.sql import func

# 交易类型常量
TRANSACTION_TYPES = {
    'INCOME': 'INCOME',    # 收入
    'EXPENSE': 'EXPENSE'   # 支出
}

# 引用类型常量 - 修改后
REFERENCE_TYPES = {
    'SALE': 'SALE',                   # 销售单 (收入)
    'PURCHASE': 'PURCHASE',           # 进货单 (支出)
    'SALE_REFUND': 'SALE_REFUND',     # 销售退款 (支出)
    'PURCHASE_RETURN': 'PURCHASE_RETURN', # 进货退货/退款 (收入)
    'SALARY': 'SALARY',               # 工资支出 (支出)
    'OTHER_INCOME': 'OTHER_INCOME',   # 其他收入
    'OTHER_EXPENSE': 'OTHER_EXPENSE'  # 其他支出
}

class Transaction(db.Model):
    """财务交易记录表"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # INCOME 或 EXPENSE
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(50))  # 关联单据编号
    reference_type = db.Column(db.String(20))  # 关联单据类型
    transaction_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # 关联用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    
    @property
    def is_income(self):
        """是否为收入"""
        return self.type == TRANSACTION_TYPES['INCOME']

