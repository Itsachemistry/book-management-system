import { defineStore } from 'pinia';
import { getSales, getSale, refundSale } from '../api/sales';

export const useSalesStore = defineStore('sales', {
  state: () => ({
    sales: [],
    currentSale: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      per_page: 20,
      total: 0,
      pages: 1
    }
  }),
  
  getters: {
    // 完成销售数量
    completedSalesCount: (state) => {
      return state.sales.filter(sale => sale.status === 'COMPLETED').length;
    },
    
    // 已退款销售数量
    refundedSalesCount: (state) => {
      return state.sales.filter(sale => sale.status === 'REFUNDED').length;
    },
    
    // 销售总金额
    totalAmount: (state) => {
      return state.sales
        .filter(sale => sale.status === 'COMPLETED')
        .reduce((sum, sale) => sum + parseFloat(sale.total_amount), 0)
        .toFixed(2);
    }
  },
  
  actions: {
    // 加载销售列表
    async loadSales(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await getSales(params);
        this.sales = response.sales;
        this.pagination = response.pagination;
      } catch (error) {
        this.error = error.message;
        console.error('加载销售列表失败:', error);
      } finally {
        this.loading = false;
      }
    },
    
    // 获取单个销售详情
    async getSale(id) {
      try {
        return await getSale(id);
      } catch (error) {
        console.error('获取销售详情失败:', error);
        throw error;
      }
    },
    
    // 处理退款
    async refundSale(id) {
      try {
        const result = await refundSale(id);
        
        // 更新本地状态
        const index = this.sales.findIndex(s => s.id === id);
        if (index !== -1) {
          this.sales[index].status = 'REFUNDED';
        }
        
        return result;
      } catch (error) {
        console.error('退款处理失败:', error);
        throw error;
      }
    },
    
    // 清除错误
    clearError() {
      this.error = null;
    }
  }
});