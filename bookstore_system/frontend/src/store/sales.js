import { defineStore } from 'pinia';
import { getSales, getSale, refundSale, createSale as createSaleApi } from '../api/sales';
import { useAuthStore } from './auth';

export const useSalesStore = defineStore('sales', {
  state: () => ({
    sales: [],
    loading: false,
    error: null,
    pagination: {
      page: 1,
      pages: 1,
      total: 0,
      per_page: 10
    }
  }),

  actions: {
    async loadSales(filters = {}) {
      this.loading = true;
      try {
        // 首先确认用户已登录
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          console.warn('尝试加载销售列表时用户未登录');
          throw new Error('需要登录才能访问销售数据');
        }
        
        const response = await getSales(filters);
        this.sales = response.sales || response.items || [];
        this.pagination = response.pagination || {
          page: 1,
          pages: 1,
          total: 0,
          per_page: 10
        };
        this.error = null;
      } catch (error) {
        console.error('加载销售列表失败:', error);
        this.error = error.message;
        this.sales = [];
      } finally {
        this.loading = false;
      }
    },

    async getSale(id) {
      try {
        // 首先确认用户已登录
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          console.warn('尝试获取销售详情时用户未登录');
          throw new Error('需要登录才能访问销售数据');
        }
        
        return await getSale(id);
      } catch (error) {
        console.error('获取销售详情失败:', error);
        throw error;
      }
    },

    async refundSale(id) {
      try {
        // 首先确认用户已登录
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          console.warn('尝试退款时用户未登录');
          throw new Error('需要登录才能处理退款');
        }
        
        const result = await refundSale(id);
        // 更新本地列表中的状态
        const index = this.sales.findIndex(sale => sale.id === id);
        if (index !== -1 && result.sale) {
          this.sales[index] = result.sale;
        }
        return result;
      } catch (error) {
        console.error('退款处理失败:', error);
        throw error;
      }
    },

    async createSale(saleData) {
      try {
        // 首先确认用户已登录
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          console.warn('尝试创建销售时用户未登录');
          throw new Error('需要登录才能创建销售记录');
        }
        
        console.log('销售Store: 创建销售前的Token状态:', !!localStorage.getItem('auth_token'));
        
        const result = await createSaleApi(saleData);
        // 创建成功后更新列表
        await this.loadSales();
        return result;
      } catch (error) {
        console.error('创建销售记录失败:', error);
        throw error;
      }
    }
  }
});