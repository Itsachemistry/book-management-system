from ..database import db
from flask import current_app
from datetime import datetime
from .. import bcrypt

class User(db.Model):
    """
    用户模型类，存储书店管理系统用户信息
    包含店员和管理员角色
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    role = db.Column(db.String(20), default='NORMAL_ADMIN', nullable=False)  # NORMAL_ADMIN 或 SUPER_ADMIN
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """设置用户密码，使用bcrypt进行哈希"""
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """验证密码是否正确"""
        return bcrypt.check_password_hash(self.hashed_password, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

