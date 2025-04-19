import { defineStore } from 'pinia';
import { 
  getOrders, 
  getOrder, 
  createOrder, 
  updateOrder, 
  payOrder, 
  returnOrder, 
  stockInOrder 
} from '../api/procurement';

export const useProcurementStore = defineStore('procurement', {
  state: () => ({
    orders: [],
    currentOrder: null,
    pagination: {
      page: 1,
      per_page: 20,
      total: 0,
      pages: 0
    },
    loading: false,
    error: null,
    filters: {
      status: null,
      start_date: null,
      end_date: null
    }
  }),
  
  getters: {
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error,
    
    // 获取不同状态的订单计数
    unpaidOrdersCount: (state) => state.orders.filter(order => order.status === 'UNPAID').length,
    paidOrdersCount: (state) => state.orders.filter(order => order.status === 'PAID').length,
    stockedOrdersCount: (state) => state.orders.filter(order => order.status === 'STOCKED').length,
    returnedOrdersCount: (state) => state.orders.filter(order => order.status === 'RETURNED').length,
    
    // 格式化的订单总金额
    formattedTotalAmount: (state) => {
      if (!state.currentOrder) return '0.00';
      return parseFloat(state.currentOrder.total_amount).toFixed(2);
    }
  },
  
  actions: {
    /**
     * 加载订单列表
     * @param {Object} params 查询参数
     */
    async loadOrders(params = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        // 合并过滤器和传入参数
        const queryParams = { ...this.filters, ...params };
        
        if (params.page) {
          this.pagination.page = params.page;
        }
        
        if (params.status !== undefined) {
          this.filters.status = params.status;
        }
        
        if (params.start_date !== undefined) {
          this.filters.start_date = params.start_date;
        }
        
        if (params.end_date !== undefined) {
          this.filters.end_date = params.end_date;
        }
        
        const result = await getOrders({
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          ...queryParams
        });
        
        this.orders = result.orders;
        this.pagination = result.pagination;
        
        return result;
      } catch (error) {
        this.error = error.message || '加载订单列表失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 加载单个订单详情
     * @param {number} id 订单ID
     */
    async loadOrder(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const order = await getOrder(id);
        this.currentOrder = order;
        return order;
      } catch (error) {
        this.error = error.message || '加载订单详情失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 创建新订单
     * @param {Object} orderData 订单数据
     */
    async addOrder(orderData) {
      this.loading = true;
      this.error = null;
      
      try {
        const order = await createOrder(orderData);
        
        // 可选：将新订单添加到列表开头
        this.orders.unshift(order);
        this.currentOrder = order;
        
        // 更新分页信息
        this.pagination.total += 1;
        this.pagination.pages = Math.ceil(this.pagination.total / this.pagination.per_page);
        
        return order;
      } catch (error) {
        this.error = error.message || '创建订单失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 更新订单基本信息
     * @param {number} id 订单ID
     * @param {Object} orderData 要更新的数据
     */
    async editOrder(id, orderData) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedOrder = await updateOrder(id, orderData);
        
        // 更新状态中的订单
        if (this.currentOrder && this.currentOrder.id === id) {
          this.currentOrder = updatedOrder;
        }
        
        // 更新列表中的订单
        const index = this.orders.findIndex(order => order.id === id);
        if (index !== -1) {
          this.orders[index] = updatedOrder;
        }
        
        return updatedOrder;
      } catch (error) {
        this.error = error.message || '更新订单失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 支付订单
     * @param {number} id 订单ID
     */
    async payOrder(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await payOrder(id);
        
        // 更新状态
        if (this.currentOrder && this.currentOrder.id === id) {
          this.currentOrder = result.order;
        }
        
        // 更新列表中的订单
        const index = this.orders.findIndex(order => order.id === id);
        if (index !== -1) {
          this.orders[index] = result.order;
        }
        
        return result;
      } catch (error) {
        this.error = error.message || '支付订单失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 退货订单
     * @param {number} id 订单ID
     */
    async returnOrder(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await returnOrder(id);
        
        // 更新状态
        if (this.currentOrder && this.currentOrder.id === id) {
          this.currentOrder = result.order;
        }
        
        // 更新列表中的订单
        const index = this.orders.findIndex(order => order.id === id);
        if (index !== -1) {
          this.orders[index] = result.order;
        }
        
        return result;
      } catch (error) {
        this.error = error.message || '退货订单失败';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 入库订单
     * @param {number} id 订单ID
     */
    async stockInOrder(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await stockInOrder(id);
        
        // 更新状态
        if (this.currentOrder && this.currentOrder.id === id) {
          this.currentOrder = result.order;
        }
        
        // 更新列表中的订单
        const index = this.orders.findIndex(order => order.id === id);
        if (index !== -1) {
          this.orders[index] = result.order;
        }
        
        return result;
      } catch (error) {
        this.error = error.message || '入库操作失败';
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
      // 更新过滤器
      this.filters = { ...this.filters, ...filters };
      
      // 重置到第一页
      this.pagination.page = 1;
      
      // 加载数据
      return this.loadOrders();
    },
    
    /**
     * 重置过滤器
     */
    resetFilters() {
      this.filters = {
        status: null,
        start_date: null,
        end_date: null
      };
      
      this.pagination.page = 1;
      
      return this.loadOrders();
    }
  }
});