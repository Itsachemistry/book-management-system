from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta
from ..models.transaction import Transaction, TRANSACTION_TYPES
from ..models.sale import Sale, SALE_STATUS
from ..models.book import Book
from ..models.purchase_order import PurchaseOrder, ORDER_STATUS
from ..database import db

class FinanceService:
    """财务服务类，用于处理财务相关的业务逻辑和数据分析"""
    
    @staticmethod
    def get_sales_statistics(start_date=None, end_date=None):
        """获取销售统计数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 销售统计数据
        """
        query = db.session.query(
            func.count(Sale.id).label('total_sales'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).filter(Sale.status == SALE_STATUS['COMPLETED'])
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
            
        result = query.first()
        
        return {
            'total_sales': result.total_sales or 0,
            'total_revenue': float(result.total_revenue or 0)
        }
    
    @staticmethod
    def get_sales_trend(period_type, limit=30, start_date=None, end_date=None):
        """获取销售趋势
        
        Arguments:
            period_type {str} -- 周期类型: 'daily', 'weekly', 或 'monthly'
            limit {int} -- 返回数据点的数量上限
            start_date {datetime} -- 开始日期
            end_date {datetime} -- 结束日期
        
        Returns:
            list -- 销售趋势数据列表
        """
        # 确定日期范围
        if end_date is None:
            end_date = datetime.now()
        
        if start_date is None:
            if period_type == 'daily':
                start_date = end_date - timedelta(days=limit - 1)
            elif period_type == 'weekly':
                start_date = end_date - timedelta(weeks=limit - 1)
            else:  # monthly
                # 向前推算指定数量的月份
                year = end_date.year
                month = end_date.month - (limit - 1)
                # 处理负月份
                while month <= 0:
                    year -= 1
                    month += 12
                start_date = datetime(year, month, 1)
        
        # 根据不同的周期类型构建查询
        result = []
        
        if period_type == 'daily':
            # 日期序列
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                next_date = current_date + timedelta(days=1)
                
                # 收入：获取该日期的所有收入
                income = db.session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.type == TRANSACTION_TYPES['INCOME'])\
                    .filter(Transaction.transaction_date >= current_date)\
                    .filter(Transaction.transaction_date < next_date)\
                    .scalar() or 0
                
                # 支出：获取该日期的所有支出
                expense = db.session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.type == TRANSACTION_TYPES['EXPENSE'])\
                    .filter(Transaction.transaction_date >= current_date)\
                    .filter(Transaction.transaction_date < next_date)\
                    .scalar() or 0
                
                result.append({
                    'period': date_str,
                    'income': float(income),
                    'expense': float(expense)
                })
                
                current_date = next_date
            
        elif period_type == 'weekly':
            # 按周统计
            # 找到起始周的星期一
            start_week = start_date - timedelta(days=start_date.weekday())
            current_week = start_week
            
            while current_week <= end_date:
                week_end = current_week + timedelta(days=6)  # 星期日
                week_str = f"{current_week.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}"
                next_week = current_week + timedelta(days=7)
                
                # 收入：获取该周的所有收入
                income = db.session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.type == TRANSACTION_TYPES['INCOME'])\
                    .filter(Transaction.transaction_date >= current_week)\
                    .filter(Transaction.transaction_date <= week_end)\
                    .scalar() or 0
                
                # 支出：获取该周的所有支出
                expense = db.session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.type == TRANSACTION_TYPES['EXPENSE'])\
                    .filter(Transaction.transaction_date >= current_week)\
                    .filter(Transaction.transaction_date <= week_end)\
                    .scalar() or 0
                
                result.append({
                    'period': week_str,
                    'income': float(income),
                    'expense': float(expense)
                })
                
                current_week = next_week
                
        else:  # monthly
            # 按月统计
            # 找到起始月的第一天
            current_month = datetime(start_date.year, start_date.month, 1)
            
            while current_month <= end_date:
                # 确定月末
                if current_month.month == 12:
                    month_end = datetime(current_month.year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = datetime(current_month.year, current_month.month + 1, 1) - timedelta(days=1)
                
                month_str = current_month.strftime('%Y-%m')
                
                # 下一个月
                if current_month.month == 12:
                    next_month = datetime(current_month.year + 1, 1, 1)
                else:
                    next_month = datetime(current_month.year, current_month.month + 1, 1)
                
                # 收入：获取该月的所有收入
                income = db.session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.type == TRANSACTION_TYPES['INCOME'])\
                    .filter(Transaction.transaction_date >= current_month)\
                    .filter(Transaction.transaction_date <= month_end)\
                    .scalar() or 0
                
                # 支出：获取该月的所有支出
                expense = db.session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.type == TRANSACTION_TYPES['EXPENSE'])\
                    .filter(Transaction.transaction_date >= current_month)\
                    .filter(Transaction.transaction_date <= month_end)\
                    .scalar() or 0
                
                result.append({
                    'period': month_str,
                    'income': float(income),
                    'expense': float(expense)
                })
                
                current_month = next_month
            
        return result
    
    @staticmethod
    def get_top_selling_books(start_date=None, end_date=None, limit=10):
        """获取畅销书籍排名
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回的数据量限制
            
        Returns:
            list: 畅销书籍列表
        """
        from ..models.sale import SaleItem
        
        # 查询销售项目，按书籍分组并计算销量
        query = db.session.query(
            Book.id,
            Book.name,
            Book.author,
            Book.isbn,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.quantity * SaleItem.price).label('total_revenue')
        ).join(
            SaleItem, SaleItem.book_id == Book.id
        ).join(
            Sale, Sale.id == SaleItem.sale_id
        ).filter(
            Sale.status == SALE_STATUS['COMPLETED']
        )
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
            
        query = query.group_by(Book.id).order_by(desc('total_quantity')).limit(limit)
        
        results = query.all()
        
        # 格式化结果
        top_books = []
        for book in results:
            top_books.append({
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'isbn': book.isbn,
                'total_quantity': book.total_quantity,
                'total_revenue': float(book.total_revenue or 0)
            })
            
        return top_books
    
    @staticmethod
    def get_revenue_by_category(start_date=None, end_date=None):
        """按分类获取销售收入统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 分类收入统计
        """
        # 注意：此方法假设Book模型有category属性
        # 如果没有，可以考虑使用其他属性如publisher或根据业务需求调整分组逻辑
        from ..models.sale import SaleItem
        
        # 按出版社分组（如果没有专门的分类字段）
        query = db.session.query(
            Book.publisher,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.quantity * SaleItem.price).label('total_revenue')
        ).join(
            SaleItem, SaleItem.book_id == Book.id
        ).join(
            Sale, Sale.id == SaleItem.sale_id
        ).filter(
            Sale.status == SALE_STATUS['COMPLETED']
        )
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
            
        query = query.group_by(Book.publisher).order_by(desc('total_revenue'))
        
        results = query.all()
        
        # 格式化结果
        categories = []
        for item in results:
            categories.append({
                'category': item.publisher or '未分类',
                'total_quantity': item.total_quantity,
                'total_revenue': float(item.total_revenue or 0)
            })
            
        return categories
    
    @staticmethod
    def get_profit_analysis(start_date=None, end_date=None):
        """利润分析
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 利润分析数据
        """
        # 获取收入（销售额）
        sales_query = db.session.query(
            func.sum(Sale.total_amount).label('total_revenue')
        ).filter(Sale.status == SALE_STATUS['COMPLETED'])
        
        if start_date:
            sales_query = sales_query.filter(Sale.sale_date >= start_date)
        
        if end_date:
            sales_query = sales_query.filter(Sale.sale_date <= end_date)
            
        total_revenue = sales_query.scalar() or 0
        
        # 获取支出（采购成本）
        purchase_query = db.session.query(
            func.sum(PurchaseOrder.total_amount).label('total_cost')
        ).filter(PurchaseOrder.status == ORDER_STATUS['PAID'])
        
        if start_date:
            purchase_query = purchase_query.filter(PurchaseOrder.order_date >= start_date)
        
        if end_date:
            purchase_query = purchase_query.filter(PurchaseOrder.order_date <= end_date)
            
        total_cost = purchase_query.scalar() or 0
        
        # 计算其他支出（从Transaction表获取）
        other_expense_query = db.session.query(
            func.sum(Transaction.amount).label('total_expense')
        ).filter(
            Transaction.type == TRANSACTION_TYPES['EXPENSE'],
            # 不包括采购支出，避免重复计算
            Transaction.reference_type != 'PURCHASE'
        )
        
        if start_date:
            other_expense_query = other_expense_query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            other_expense_query = other_expense_query.filter(Transaction.transaction_date <= end_date)
            
        other_expenses = other_expense_query.scalar() or 0
        
        # 计算毛利和净利
        gross_profit = float(total_revenue) - float(total_cost)
        net_profit = gross_profit - float(other_expenses)
        
        # 计算利润率
        gross_margin = (gross_profit / float(total_revenue)) * 100 if total_revenue > 0 else 0
        net_margin = (net_profit / float(total_revenue)) * 100 if total_revenue > 0 else 0
        
        return {
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'other_expenses': float(other_expenses),
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'gross_margin': gross_margin,
            'net_margin': net_margin
        }

