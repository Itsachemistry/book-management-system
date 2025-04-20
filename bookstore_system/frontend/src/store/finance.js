import { defineStore } from 'pinia';
import { getTransactions, getFinanceSummary } from '../api/finance';

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
    formattedNetProfit: (state) => parseFloat(state.summary.net_profit).toFixed(2)
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
    }
  }
});