import { defineStore } from 'pinia';
import { getTransactions, getFinanceSummary, getFinanceTrend, getSalesStatistics, 
         getTopSellingBooks, getProfitAnalysis, getRevenueByCategory } from '../api/finance';

export const useFinanceStore = defineStore('finance', {
  state: () => ({
    transactions: [],
    summary: {
      total_income: 0,
      total_expense: 0,
      net_profit: 0,
      today_income: 0,
      month_income: 0,
      by_type: {}
    },
    loading: false,
    error: null,
    pagination: {
      total: 0,
      pages: 0,
      page: 1,
      per_page: 10
    },
    filters: {
      transaction_type: '',
      start_date: '',
      end_date: ''
    },
    // 新增报表相关数据
    reports: {
      trend: {
        labels: [],
        income: [],
        expense: []
      },
      salesStatistics: {
        total_sales: 0,
        total_items_sold: 0,
        average_sale_value: 0,
        sales_by_date: []
      },
      topSellingBooks: [],
      profitAnalysis: {
        total_revenue: 0,
        total_cost: 0,
        gross_profit: 0,
        profit_margin: 0,
        monthly_breakdown: []
      },
      revenueByCategory: []
    },
    reportFilters: {
      period: 'daily',
      limit: 30,
      start_date: '',
      end_date: ''
    }
  }),
  
  getters: {
    // 总收入
    totalIncome: (state) => state.summary.total_income,
    
    // 总支出
    totalExpense: (state) => state.summary.total_expense,
    
    // 净利润
    netProfit: (state) => state.summary.net_profit,
    
    // 格式化的总收入
    formattedTotalIncome: (state) => parseFloat(state.summary.total_income).toFixed(2),
    
    // 格式化的总支出
    formattedTotalExpense: (state) => parseFloat(state.summary.total_expense).toFixed(2),
    
    // 格式化的净利润
    formattedNetProfit: (state) => parseFloat(state.summary.net_profit).toFixed(2),
    
    // 报表相关的getter
    
    // 格式化后的销售趋势数据，适用于图表组件
    salesTrendChartData: (state) => {
      return {
        labels: state.reports.trend.labels,
        datasets: [
          {
            label: '收入',
            data: state.reports.trend.income,
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            fill: true
          },
          {
            label: '支出',
            data: state.reports.trend.expense,
            borderColor: '#F44336',
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            fill: true
          }
        ]
      };
    },
    
    // 格式化后的收入分类数据，适用于饼图
    revenueByCategoryChartData: (state) => {
      if (!state.reports.revenueByCategory.length) return { labels: [], datasets: [] };
      
      return {
        labels: state.reports.revenueByCategory.map(item => item.category),
        datasets: [{
          data: state.reports.revenueByCategory.map(item => item.amount),
          backgroundColor: [
            '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', 
            '#E91E63', '#F44336', '#CDDC39', '#3F51B5'
          ]
        }]
      };
    },
    
    // 利润率格式化（百分比）
    formattedProfitMargin: (state) => {
      const margin = state.reports.profitAnalysis.profit_margin;
      return `${(margin * 100).toFixed(2)}%`;
    },
    
    // 获取畅销书籍排行数据
    topBooks: (state) => state.reports.topSellingBooks,
    
    // 获取报表时间范围
    reportDateRange: (state) => {
      return {
        start: state.reportFilters.start_date,
        end: state.reportFilters.end_date
      };
    }
  },
  
  actions: {
    /**
     * 加载交易记录列表
     * @param {Object} params 查询参数
     */
    async loadTransactions(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        // 合并过滤器和传入参数
        const queryParams = { ...this.filters, ...params };
        
        if (params.page) {
          this.pagination.page = params.page;
        }
        
        if (params.transaction_type !== undefined) {
          this.filters.transaction_type = params.transaction_type;
        }
        
        if (params.start_date !== undefined) {
          this.filters.start_date = params.start_date;
        }
        
        if (params.end_date !== undefined) {
          this.filters.end_date = params.end_date;
        }
        
        const result = await getTransactions({
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          ...queryParams
        });
        
        this.transactions = result.transactions;
        this.pagination = result.pagination;
        
        return result;
      } catch (error) {
        this.error = error.message || '加载交易记录失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载财务摘要
     */
    async loadSummary() {
      this.loading = true;
      this.error = null;
      
      try {
        const summary = await getFinanceSummary();
        this.summary = summary;
        return summary;
      } catch (error) {
        this.error = error.message || '加载财务摘要失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 应用过滤器并重新加载数据
     * @param {Object} filters 过滤条件
     */
    async applyFilters(filters) {
      this.filters = { ...this.filters, ...filters };
      this.pagination.page = 1; // 重置到第一页
      return this.loadTransactions();
    },
    
    /**
     * 加载销售趋势数据
     * @param {Object} params 查询参数, 包含period, limit, start_date, end_date等
     */
    async loadSalesTrend(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        // 更新报表过滤器
        if (params.period) {
          this.reportFilters.period = params.period;
        }
        
        if (params.limit) {
          this.reportFilters.limit = params.limit;
        }
        
        if (params.start_date !== undefined) {
          this.reportFilters.start_date = params.start_date;
        }
        
        if (params.end_date !== undefined) {
          this.reportFilters.end_date = params.end_date;
        }
        
        const result = await getFinanceTrend({
          period: this.reportFilters.period,
          limit: this.reportFilters.limit,
          start_date: this.reportFilters.start_date,
          end_date: this.reportFilters.end_date
        });
        
        this.reports.trend = result;
        return result;
      } catch (error) {
        this.error = error.message || '加载销售趋势数据失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载销售统计数据
     * @param {Object} params 查询参数, 包含start_date, end_date
     */
    async loadSalesStatistics(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const queryParams = { ...params };
        
        if (params.start_date !== undefined) {
          this.reportFilters.start_date = params.start_date;
        } else if (this.reportFilters.start_date) {
          queryParams.start_date = this.reportFilters.start_date;
        }
        
        if (params.end_date !== undefined) {
          this.reportFilters.end_date = params.end_date;
        } else if (this.reportFilters.end_date) {
          queryParams.end_date = this.reportFilters.end_date;
        }
        
        const result = await getSalesStatistics(queryParams);
        this.reports.salesStatistics = result;
        return result;
      } catch (error) {
        this.error = error.message || '加载销售统计数据失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载畅销书籍排行榜
     * @param {Object} params 查询参数, 包含start_date, end_date, limit
     */
    async loadTopSellingBooks(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const queryParams = { ...params };
        
        if (params.limit === undefined && this.reportFilters.limit) {
          queryParams.limit = this.reportFilters.limit;
        }
        
        if (params.start_date === undefined && this.reportFilters.start_date) {
          queryParams.start_date = this.reportFilters.start_date;
        }
        
        if (params.end_date === undefined && this.reportFilters.end_date) {
          queryParams.end_date = this.reportFilters.end_date;
        }
        
        const result = await getTopSellingBooks(queryParams);
        this.reports.topSellingBooks = result;
        return result;
      } catch (error) {
        this.error = error.message || '加载畅销书籍排行榜失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载利润分析数据
     * @param {Object} params 查询参数, 包含start_date, end_date
     */
    async loadProfitAnalysis(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const queryParams = { ...params };
        
        if (params.start_date === undefined && this.reportFilters.start_date) {
          queryParams.start_date = this.reportFilters.start_date;
        }
        
        if (params.end_date === undefined && this.reportFilters.end_date) {
          queryParams.end_date = this.reportFilters.end_date;
        }
        
        const result = await getProfitAnalysis(queryParams);
        this.reports.profitAnalysis = result;
        return result;
      } catch (error) {
        this.error = error.message || '加载利润分析数据失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载按分类的收入报表
     * @param {Object} params 查询参数, 包含start_date, end_date
     */
    async loadRevenueByCategory(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const queryParams = { ...params };
        
        if (params.start_date === undefined && this.reportFilters.start_date) {
          queryParams.start_date = this.reportFilters.start_date;
        }
        
        if (params.end_date === undefined && this.reportFilters.end_date) {
          queryParams.end_date = this.reportFilters.end_date;
        }
        
        const result = await getRevenueByCategory(queryParams);
        this.reports.revenueByCategory = result;
        return result;
      } catch (error) {
        this.error = error.message || '加载分类收入报表失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 更新报表日期范围并重新加载所有报表数据
     * @param {Object} dateRange 日期范围 {start_date, end_date}
     */
    async updateReportDateRange(dateRange) {
      this.reportFilters.start_date = dateRange.start_date;
      this.reportFilters.end_date = dateRange.end_date;
      
      // 并行加载所有报表数据
      return Promise.all([
        this.loadSalesTrend(),
        this.loadSalesStatistics(),
        this.loadTopSellingBooks(),
        this.loadProfitAnalysis(),
        this.loadRevenueByCategory()
      ]);
    },
    
    /**
     * 重置报表过滤器
     */
    resetReportFilters() {
      this.reportFilters = {
        period: 'daily',
        limit: 30,
        start_date: '',
        end_date: ''
      };
    }
  }
});