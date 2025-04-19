<template>
  <div class="procurement-view">
    <h1>图书进货管理</h1>
    
    <!-- 过滤器部分 -->
    <div class="filter-section">
      <div class="filter-controls">
        <div class="filter-row">
          <div class="filter-item">
            <label for="status">订单状态:</label>
            <select v-model="filters.status" id="status" class="form-control">
              <option value="">全部</option>
              <option value="UNPAID">未支付</option>
              <option value="PAID">已支付</option>
              <option value="STOCKED">已入库</option>
              <option value="RETURNED">已退货</option>
            </select>
          </div>
          
          <div class="filter-item">
            <label for="start-date">开始日期:</label>
            <input
              type="date"
              id="start-date"
              v-model="filters.start_date"
              class="form-control"
            />
          </div>
          
          <div class="filter-item">
            <label for="end-date">结束日期:</label>
            <input
              type="date"
              id="end-date"
              v-model="filters.end_date"
              class="form-control"
            />
          </div>
          
          <div class="filter-actions">
            <button class="btn btn-primary" @click="applyFilters">应用过滤</button>
            <button class="btn btn-secondary" @click="resetFilters">重置</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 订单状态统计卡片 -->
    <div class="status-cards">
      <div class="status-card">
        <h3>未支付订单</h3>
        <div class="count">{{ procurementStore.unpaidOrdersCount }}</div>
      </div>
      <div class="status-card">
        <h3>已支付订单</h3>
        <div class="count">{{ procurementStore.paidOrdersCount }}</div>
      </div>
      <div class="status-card">
        <h3>已入库订单</h3>
        <div class="count">{{ procurementStore.stockedOrdersCount }}</div>
      </div>
      <div class="status-card">
        <h3>已退货订单</h3>
        <div class="count">{{ procurementStore.returnedOrdersCount }}</div>
      </div>
    </div>
    
    <!-- 创建新订单按钮 -->
    <div class="actions-section">
      <button class="btn btn-success" @click="showCreateOrderForm">
        <i class="fas fa-plus"></i> 创建新进货单
      </button>
    </div>
    
    <!-- 订单列表 -->
    <div class="orders-section">
      <div v-if="procurementStore.loading" class="loading">
        <div class="spinner"></div>
        <p>正在加载订单数据...</p>
      </div>
      
      <div v-else-if="procurementStore.error" class="error-message">
        <p>{{ procurementStore.error }}</p>
        <button @click="loadOrders" class="btn btn-secondary">重试</button>
      </div>
      
      <div v-else-if="!procurementStore.orders.length" class="no-data">
        <p>暂无进货订单数据</p>
      </div>
      
      <table v-else class="orders-table">
        <thead>
          <tr>
            <th>订单号</th>
            <th>日期</th>
            <th>供应商</th>
            <th>总金额</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in procurementStore.orders" :key="order.id">
            <td>{{ order.order_number }}</td>
            <td>{{ formatDate(order.order_date) }}</td>
            <td>{{ order.supplier || '未指定' }}</td>
            <td>￥{{ formatCurrency(order.total_amount) }}</td>
            <td>
              <span :class="['status-badge', `status-${order.status.toLowerCase()}`]">
                {{ translateStatus(order.status) }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-info btn-sm" @click="viewOrderDetail(order.id)">
                  查看
                </button>
                <button 
                  v-if="order.status === 'UNPAID'" 
                  class="btn btn-primary btn-sm" 
                  @click="handlePay(order.id)"
                >
                  支付
                </button>
                <button 
                  v-if="order.status === 'UNPAID'" 
                  class="btn btn-danger btn-sm" 
                  @click="handleReturn(order.id)"
                >
                  退货
                </button>
                <button 
                  v-if="order.status === 'PAID'" 
                  class="btn btn-success btn-sm" 
                  @click="handleStockIn(order.id)"
                >
                  入库
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 分页控件 -->
      <div class="pagination" v-if="procurementStore.orders.length">
        <button 
          :disabled="procurementStore.pagination.page === 1" 
          @click="goToPage(procurementStore.pagination.page - 1)"
          class="btn btn-sm"
        >
          上一页
        </button>
        
        <span class="page-info">
          第 {{ procurementStore.pagination.page }} 页，共 {{ procurementStore.pagination.pages }} 页
        </span>
        
        <button 
          :disabled="procurementStore.pagination.page >= procurementStore.pagination.pages" 
          @click="goToPage(procurementStore.pagination.page + 1)"
          class="btn btn-sm"
        >
          下一页
        </button>
      </div>
    </div>
    
    <!-- 订单详情对话框 -->
    <div v-if="showOrderDetail" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>订单详情</h2>
          <button class="close-btn" @click="closeOrderDetail">&times;</button>
        </div>
        <div class="modal-body" v-if="currentOrder">
          <div class="order-info">
            <p><strong>订单号:</strong> {{ currentOrder.order_number }}</p>
            <p><strong>日期:</strong> {{ formatDate(currentOrder.order_date) }}</p>
            <p><strong>供应商:</strong> {{ currentOrder.supplier || '未指定' }}</p>
            <p><strong>状态:</strong> {{ translateStatus(currentOrder.status) }}</p>
            <p><strong>总金额:</strong> ￥{{ formatCurrency(currentOrder.total_amount) }}</p>
            <p v-if="currentOrder.remarks"><strong>备注:</strong> {{ currentOrder.remarks }}</p>
          </div>
          
          <h3>订单项目</h3>
          <table class="items-table">
            <thead>
              <tr>
                <th>ISBN/标题</th>
                <th>作者</th>
                <th>出版社</th>
                <th>数量</th>
                <th>单价</th>
                <th>小计</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentOrder.items" :key="item.id">
                <td>{{ item.book ? item.book.isbn : item.isbn }}<br/>{{ item.book ? item.book.name : item.title }}</td>
                <td>{{ item.book ? item.book.author : item.author }}</td>
                <td>{{ item.book ? item.book.publisher : item.publisher }}</td>
                <td>{{ item.quantity }}</td>
                <td>￥{{ formatCurrency(item.purchase_price) }}</td>
                <td>￥{{ formatCurrency(item.quantity * item.purchase_price) }}</td>
              </tr>
            </tbody>
          </table>
          
          <div class="order-actions" v-if="currentOrder.status === 'UNPAID'">
            <button class="btn btn-primary" @click="handlePay(currentOrder.id)">支付订单</button>
            <button class="btn btn-danger" @click="handleReturn(currentOrder.id)">退货</button>
          </div>
          <div class="order-actions" v-if="currentOrder.status === 'PAID'">
            <button class="btn btn-success" @click="handleStockIn(currentOrder.id)">入库</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建订单对话框 -->
    <div v-if="showCreateForm" class="modal">
      <div class="modal-content modal-lg">
        <div class="modal-header">
          <h2>创建新进货单</h2>
          <button class="close-btn" @click="closeCreateForm">&times;</button>
        </div>
        <div class="modal-body">
          <OrderForm @created="onOrderCreated" @cancel="closeCreateForm" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue';
import { useProcurementStore } from '../store/procurement';
import OrderForm from '../components/OrderForm.vue';

export default {
  name: 'ProcurementView',
  components: {
    OrderForm
  },
  setup() {
    const procurementStore = useProcurementStore();
    
    // 状态变量
    const filters = reactive({
      status: '',
      start_date: '',
      end_date: ''
    });
    
    const showOrderDetail = ref(false);
    const showCreateForm = ref(false);
    const currentOrder = ref(null);
    
    // 加载订单数据
    const loadOrders = async () => {
      try {
        await procurementStore.loadOrders();
      } catch (error) {
        console.error('Failed to load orders:', error);
      }
    };
    
    // 页面初始化时加载数据
    onMounted(() => {
      loadOrders();
    });
    
    // 过滤方法
    const applyFilters = async () => {
      try {
        await procurementStore.applyFilters(filters);
      } catch (error) {
        console.error('Failed to apply filters:', error);
      }
    };
    
    const resetFilters = () => {
      filters.status = '';
      filters.start_date = '';
      filters.end_date = '';
      procurementStore.resetFilters();
    };
    
    // 分页方法
    const goToPage = (page) => {
      procurementStore.loadOrders({ page });
    };
    
    // 订单操作方法
    const viewOrderDetail = async (orderId) => {
      try {
        const order = await procurementStore.loadOrder(orderId);
        currentOrder.value = order;
        showOrderDetail.value = true;
      } catch (error) {
        console.error('Failed to load order details:', error);
      }
    };
    
    const closeOrderDetail = () => {
      showOrderDetail.value = false;
      currentOrder.value = null;
    };
    
    const showCreateOrderForm = () => {
      showCreateForm.value = true;
    };
    
    const closeCreateForm = () => {
      showCreateForm.value = false;
    };
    
    const onOrderCreated = (order) => {
      closeCreateForm();
      loadOrders(); // 刷新列表
    };
    
    // 处理支付、退货、入库操作
    const handlePay = async (orderId) => {
      if (!confirm('确认支付该订单？')) return;
      
      try {
        await procurementStore.payOrder(orderId);
        if (showOrderDetail.value && currentOrder.value) {
          // 如果当前显示的是此订单，刷新订单详情
          viewOrderDetail(orderId);
        }
      } catch (error) {
        console.error('Failed to pay order:', error);
        alert('支付订单失败: ' + error.message);
      }
    };
    
    const handleReturn = async (orderId) => {
      if (!confirm('确认退货？退货后将无法恢复。')) return;
      
      try {
        await procurementStore.returnOrder(orderId);
        if (showOrderDetail.value && currentOrder.value) {
          viewOrderDetail(orderId);
        }
      } catch (error) {
        console.error('Failed to return order:', error);
        alert('退货失败: ' + error.message);
      }
    };
    
    const handleStockIn = async (orderId) => {
      if (!confirm('确认将订单商品入库？入库后将增加相应图书的库存。')) return;
      
      try {
        await procurementStore.stockInOrder(orderId);
        if (showOrderDetail.value && currentOrder.value) {
          viewOrderDetail(orderId);
        }
      } catch (error) {
        console.error('Failed to stock in:', error);
        alert('入库失败: ' + error.message);
      }
    };
    
    // 工具函数
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    const formatCurrency = (value) => {
      return parseFloat(value).toFixed(2);
    };
    
    const translateStatus = (status) => {
      const statusMap = {
        'UNPAID': '未支付',
        'PAID': '已支付',
        'RETURNED': '已退货',
        'STOCKED': '已入库'
      };
      return statusMap[status] || status;
    };
    
    return {
      procurementStore,
      filters,
      showOrderDetail,
      showCreateForm,
      currentOrder,
      loadOrders,
      applyFilters,
      resetFilters,
      goToPage,
      viewOrderDetail,
      closeOrderDetail,
      showCreateOrderForm,
      closeCreateForm,
      onOrderCreated,
      handlePay,
      handleReturn,
      handleStockIn,
      formatDate,
      formatCurrency,
      translateStatus
    };
  }
};
</script>

<style scoped>
.procurement-view {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

.filter-section {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.filter-item {
  flex: 1;
  min-width: 200px;
}

.filter-actions {
  display: flex;
  gap: 10px;
}

.status-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.status-card {
  flex: 1;
  background-color: #fff;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 15px;
  text-align: center;
}

.status-card h3 {
  margin-top: 0;
  font-size: 16px;
  color: #666;
}

.status-card .count {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.actions-section {
  margin: 20px 0;
  display: flex;
  justify-content: flex-end;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.orders-table th,
.orders-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.orders-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-unpaid {
  background-color: #ffebcd;
  color: #c76e00;
}

.status-paid {
  background-color: #e0f7fa;
  color: #0288d1;
}

.status-stocked {
  background-color: #e8f5e9;
  color: #388e3c;
}

.status-returned {
  background-color: #ffebee;
  color: #d32f2f;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 5px;
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-lg {
  max-width: 1000px;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.order-info {
  margin-bottom: 20px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.items-table th,
.items-table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.order-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #d32f2f;
  padding: 20px;
  text-align: center;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.page-info {
  color: #666;
}

/* 表单控件样式 */
.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
}

.btn-primary:hover {
  background-color: #1565c0;
}

.btn-secondary {
  background-color: #757575;
  color: white;
}

.btn-secondary:hover {
  background-color: #616161;
}

.btn-success {
  background-color: #43a047;
  color: white;
}

.btn-success:hover {
  background-color: #388e3c;
}

.btn-danger {
  background-color: #e53935;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

.btn-info {
  background-color: #0288d1;
  color: white;
}

.btn-info:hover {
  background-color: #0277bd;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>