from flask import Blueprint, request, jsonify, g, abort
from ..models.transaction import Transaction, TRANSACTION_TYPES
from ..schemas.transaction_schema import TransactionSchema, TransactionQuerySchema
from ..utils.decorators import login_required, admin_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from ..database import db
from ..services.finance_service import FinanceService

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
    if 'transaction_type' in query_params and query_params['transaction_type']:
        query = query.filter(Transaction.type == query_params['transaction_type'])
    
    if 'start_date' in query_params:
        # 确保start_date是datetime对象
        start_date = query_params['start_date']
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
        query = query.filter(Transaction.transaction_date >= start_date)
    
    if 'end_date' in query_params:
        # 确保end_date是datetime对象
        end_date = query_params['end_date']
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天结束时间
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
        else:
            # 如果已经是datetime对象，仍需设置为一天结束
            end_date = end_date.replace(hour=23, minute=59, second=59)
            
        query = query.filter(Transaction.transaction_date <= end_date)
    
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
    # 解析查询参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 处理日期参数
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
    
    # 当前日期
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)
    
    # 构建查询基础
    query_income = Transaction.query.filter(Transaction.type == TRANSACTION_TYPES['INCOME'])
    query_expense = Transaction.query.filter(Transaction.type == TRANSACTION_TYPES['EXPENSE'])
    
    # 应用日期过滤
    if start_date:
        query_income = query_income.filter(Transaction.transaction_date >= start_date)
        query_expense = query_expense.filter(Transaction.transaction_date >= start_date)
    
    if end_date:
        query_income = query_income.filter(Transaction.transaction_date <= end_date)
        query_expense = query_expense.filter(Transaction.transaction_date <= end_date)
    
    # 总收入和支出
    income = query_income.with_entities(func.sum(Transaction.amount)).scalar() or 0
    expense = query_expense.with_entities(func.sum(Transaction.amount)).scalar() or 0
    
    # 今日收入
    today_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.type == TRANSACTION_TYPES['INCOME'],
        Transaction.transaction_date >= today
    ).scalar() or 0
    
    # 本月收入
    month_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.type == TRANSACTION_TYPES['INCOME'],
        Transaction.transaction_date >= month_start
    ).scalar() or 0
    
    # 按类型汇总
    summary_by_type = {}
    for t_type in TRANSACTION_TYPES.values():
        query = Transaction.query.filter(Transaction.type == t_type)
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        amount = query.with_entities(func.sum(Transaction.amount)).scalar() or 0
        summary_by_type[t_type] = float(amount)
    
    # 计算环比数据
    comparison = {}
    
    if start_date and end_date:
        # 计算上一个相同时间段
        period_length = (end_date - start_date).days
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_length)
        
        # 上一时间段收入
        prev_income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.type == TRANSACTION_TYPES['INCOME'],
            Transaction.transaction_date >= prev_start,
            Transaction.transaction_date <= prev_end
        ).scalar() or 0
        
        # 上一时间段支出
        prev_expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.type == TRANSACTION_TYPES['EXPENSE'],
            Transaction.transaction_date >= prev_start,
            Transaction.transaction_date <= prev_end
        ).scalar() or 0
        
        # 计算环比变化率
        income_change_rate = calculate_change_rate(float(income), float(prev_income))
        expense_change_rate = calculate_change_rate(float(expense), float(prev_expense))
        profit_change_rate = calculate_change_rate(
            float(income - expense), 
            float(prev_income - prev_expense)
        )
        
        comparison = {
            'income_change_rate': income_change_rate,
            'expense_change_rate': expense_change_rate,
            'profit_change_rate': profit_change_rate
        }
    
    return jsonify({
        'total_income': float(income),
        'total_expense': float(expense),
        'net_profit': float(income - expense),
        'today_income': float(today_income),
        'month_income': float(month_income),
        'by_type': summary_by_type,
        'comparison': comparison
    })


# 辅助函数：计算变化率
def calculate_change_rate(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return round((current - previous) / previous * 100, 2)


@finance_bp.route('/reports/sales-statistics', methods=['GET'])
@admin_required
def get_sales_statistics():
    """获取销售统计报表"""
    try:
        # 解析查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 转换日期字符串为日期对象
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天结束时间
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
        
        # 获取统计数据
        statistics = FinanceService.get_sales_statistics(start_date, end_date)
        
        return jsonify(statistics)
    except Exception as e:
        return jsonify({'error': f'获取销售统计失败: {str(e)}'}), 500


@finance_bp.route('/reports/sales-trend', methods=['GET'])
@admin_required
def get_sales_trend():
    """获取销售趋势报表"""
    try:
        # 解析查询参数
        period_type = request.args.get('period', 'daily')
        limit = request.args.get('limit', 30, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 验证参数
        if period_type not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': '周期类型必须是daily、weekly或monthly'}), 400
        
        if limit <= 0 or limit > 365:
            return jsonify({'error': '数据点数量必须在1到365之间'}), 400
        
        # 转换日期字符串为日期对象
        parsed_start_date = None
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
                
        parsed_end_date = None
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天结束时间
                parsed_end_date = parsed_end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
        
        # 获取趋势数据，传递转换后的日期参数
        trend_data = FinanceService.get_sales_trend(
            period_type, 
            limit,
            parsed_start_date,
            parsed_end_date
        )
        
        return jsonify(trend_data)
    except Exception as e:
        print(f"获取销售趋势数据失败: {str(e)}")
        return jsonify({'error': f'获取销售趋势失败: {str(e)}'}), 500


@finance_bp.route('/reports/top-selling-books', methods=['GET'])
@admin_required
def get_top_selling_books():
    """获取畅销书籍排行榜"""
    try:
        # 解析查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 10, type=int)
        
        # 转换日期字符串为日期对象
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天结束时间
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
        
        # 获取畅销书籍数据
        top_books = FinanceService.get_top_selling_books(start_date, end_date, limit)
        
        return jsonify(top_books)
    except Exception as e:
        return jsonify({'error': f'获取畅销书籍排行榜失败: {str(e)}'}), 500


@finance_bp.route('/reports/profit-analysis', methods=['GET'])
@admin_required
def get_profit_analysis():
    """获取利润分析报表"""
    try:
        # 解析查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 转换日期字符串为日期对象
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天结束时间
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
        
        # 获取利润分析数据
        profit_data = FinanceService.get_profit_analysis(start_date, end_date)
        
        return jsonify(profit_data)
    except Exception as e:
        return jsonify({'error': f'获取利润分析失败: {str(e)}'}), 500


@finance_bp.route('/reports/revenue-by-category', methods=['GET'])
@admin_required
def get_revenue_by_category():
    """获取按分类的收入报表"""
    try:
        # 解析查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 转换日期字符串为日期对象
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': '开始日期格式无效，应为YYYY-MM-DD'}), 400
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天结束时间
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': '结束日期格式无效，应为YYYY-MM-DD'}), 400
        
        # 获取分类收入数据
        category_data = FinanceService.get_revenue_by_category(start_date, end_date)
        
        return jsonify(category_data)
    except Exception as e:
        return jsonify({'error': f'获取分类收入报表失败: {str(e)}'}), 500

