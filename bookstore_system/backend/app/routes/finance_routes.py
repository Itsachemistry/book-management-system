from flask import Blueprint, request, jsonify, g, abort
from ..models.transaction import Transaction, TRANSACTION_TYPES
from ..schemas.transaction_schema import TransactionSchema, TransactionQuerySchema
from ..utils.decorators import login_required, admin_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from ..database import db  # 添加这一行导入db

# 创建蓝图
finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/transactions', methods=['GET'])
@admin_required
def get_transactions():
    """获取财务交易记录列表
    
    支持筛选:
    - 按交易类型
    - 按日期范围
    """
    # 解析查询参数
    schema = TransactionQuerySchema()
    try:
        query_params = schema.load(request.args)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    page = query_params.get('page', 1)
    per_page = query_params.get('per_page', 10)
    
    # 构建查询
    query = Transaction.query
    
    # 应用过滤
    if 'transaction_type' in query_params:
        query = query.filter(Transaction.transaction_type == query_params['transaction_type'])
    
    if 'start_date' in query_params:
        query = query.filter(Transaction.transaction_date >= query_params['start_date'])
    
    if 'end_date' in query_params:
        query = query.filter(Transaction.transaction_date <= query_params['end_date'])
    
    # 排序和分页
    query = query.order_by(Transaction.transaction_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 序列化结果
    schema = TransactionSchema(many=True)
    return jsonify({
        'transactions': schema.dump(pagination.items),
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page
        }
    })


@finance_bp.route('/summary', methods=['GET'])
@admin_required
def get_summary():
    """获取财务摘要
    
    返回:
    - 总收入
    - 总支出
    - 今日收入
    - 本月收入
    - 各交易类型汇总
    """
    # 当前日期
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)
    
    # 总收入和支出
    income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(Transaction.transaction_type == TRANSACTION_TYPES['INCOME']).scalar() or 0
    
    expense = db.session.query(
        func.sum(Transaction.amount)
    ).filter(Transaction.transaction_type == TRANSACTION_TYPES['EXPENSE']).scalar() or 0
    
    # 今日收入
    today_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.transaction_type == TRANSACTION_TYPES['INCOME'],
        Transaction.transaction_date >= today
    ).scalar() or 0
    
    # 本月收入
    month_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.transaction_type == TRANSACTION_TYPES['INCOME'],
        Transaction.transaction_date >= month_start
    ).scalar() or 0
    
    # 按类型汇总
    summary_by_type = {}
    for t_type in TRANSACTION_TYPES.values():
        amount = db.session.query(
            func.sum(Transaction.amount)
        ).filter(Transaction.transaction_type == t_type).scalar() or 0
        
        summary_by_type[t_type] = float(amount)
    
    return jsonify({
        'total_income': float(income),
        'total_expense': float(expense),
        'net_profit': float(income - expense),
        'today_income': float(today_income),
        'month_income': float(month_income),
        'by_type': summary_by_type
    })

