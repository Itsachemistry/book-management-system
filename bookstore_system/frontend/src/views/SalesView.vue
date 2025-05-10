<template>
  <div class="sales-view">
    <div class="header">
      <h1>销售管理</h1>
      <div class="actions">
        <button class="btn btn-primary" @click="checkBeforeCreateSale">
          新建销售
        </button>
      </div>
    </div>
    
    <!-- 筛选器 -->
    <div class="filters">
      <div class="filter-section">
        <label>状态:</label>
        <select v-model="filters.status" @change="applyFilters">
          <option value="">全部</option>
          <option value="COMPLETED">已完成</option>
          <option value="REFUNDED">已退款</option>
          <option value="CANCELLED">已取消</option>
        </select>
      </div>
      
      <div class="filter-section">
        <label>日期范围:</label>
        <input 
          type="date" 
          v-model="filters.start_date" 
          @input="applyFilters"
        />
        <span>至</span>
        <input 
          type="date" 
          v-model="filters.end_date" 
          @input="applyFilters"
        />
      </div>
    </div>
    
    <!-- 销售列表 -->
    <div class="sales-list" v-if="!salesStore.loading">
      <table class="sales-table">
        <thead>
          <tr>
            <th>销售单号</th>
            <th>日期</th>
            <th>客户</th>
            <th>金额</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sale in salesStore.sales" :key="sale.id">
            <td>{{ sale.sale_number }}</td>
            <td>{{ formatDate(sale.sale_date) }}</td>
            <td>{{ sale.customer_name || '无名客户' }}</td>
            <td>￥{{ parseFloat(sale.total_amount).toFixed(2) }}</td>
            <td>
              <span :class="'status-badge ' + sale.status.toLowerCase()">
                {{ getStatusText(sale.status) }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-info" @click="viewDetail(sale.id)">
                查看
              </button>
              <button 
                class="btn btn-sm btn-warning" 
                @click="handleRefund(sale.id)"
                v-if="sale.status === 'COMPLETED' && hasRefundPermission"
                title="退款"
              >
                退款
              </button>
            </td>
          </tr>
          <tr v-if="salesStore.sales.length === 0">
            <td colspan="6" class="no-data">暂无销售记录</td>
          </tr>
        </tbody>
      </table>
      
      <!-- 分页 -->
      <div class="pagination" v-if="salesStore.pagination.total > 0">
        <button 
          class="page-btn" 
          :disabled="salesStore.pagination.page === 1"
          @click="changePage(salesStore.pagination.page - 1)"
        >
          上一页
        </button>
        <span class="page-info">
          {{ salesStore.pagination.page }} / {{ salesStore.pagination.pages }}
        </span>
        <button 
          class="page-btn" 
          :disabled="salesStore.pagination.page >= salesStore.pagination.pages"
          @click="changePage(salesStore.pagination.page + 1)"
        >
          下一页
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-else class="loading">
      <p>加载中...</p>
    </div>
    
    <!-- 详情模态框 -->
    <div v-if="showDetailModal" class="modal">
      <div class="modal-content modal-lg">
        <div class="modal-header">
          <h2>销售详情</h2>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="currentSale">
          <!-- 销售基本信息 -->
          <div class="sale-info">
            <div class="info-row">
              <div class="info-item">
                <label>销售单号:</label>
                <span>{{ currentSale.sale_number }}</span>
              </div>
              <div class="info-item">
                <label>销售日期:</label>
                <span>{{ formatDate(currentSale.sale_date) }}</span>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-item">
                <label>客户:</label>
                <span>{{ currentSale.customer_name || '无名客户' }}</span>
              </div>
              <div class="info-item">
                <label>状态:</label>
                <span :class="'status-badge ' + currentSale.status.toLowerCase()">
                  {{ getStatusText(currentSale.status) }}
                </span>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-item">
                <label>联系方式:</label>
                <span>{{ currentSale.contact || '未提供' }}</span>
              </div>
              <div class="info-item">
                <label>支付方式:</label>
                <span>{{ getPaymentMethodText(currentSale.payment_method) }}</span>
              </div>
            </div>
            
            <div class="info-row" v-if="currentSale.remarks">
              <div class="info-item full-width">
                <label>备注:</label>
                <span>{{ currentSale.remarks }}</span>
              </div>
            </div>
          </div>
          
          <!-- 销售商品列表 -->
          <h3>销售商品</h3>
          <table class="detail-table">
            <thead>
              <tr>
                <th>书名</th>
                <th>ISBN</th>
                <th>单价</th>
                <th>数量</th>
                <th>小计</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentSale.items" :key="item.id">
                <td>{{ item.book ? item.book.name : '未知书籍' }}</td>
                <td>{{ item.book ? item.book.isbn : '-' }}</td>
                <td>￥{{ parseFloat(item.price).toFixed(2) }}</td>
                <td>{{ item.quantity }}</td>
                <td>￥{{ (parseFloat(item.price) * item.quantity).toFixed(2) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="4" class="total-label">总计:</td>
                <td class="total-amount">￥{{ parseFloat(currentSale.total_amount).toFixed(2) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>

    <!-- 创建销售表单模态框 -->
    <div v-if="showCreateForm" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>新建销售</h2>
          <button class="close-btn" @click="showCreateForm = false">&times;</button>
        </div>
        <div class="modal-body">
          <SaleForm @created="handleSaleCreated" @cancel="showCreateForm = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useSalesStore } from '../store/sales';
import { useAuthStore } from '../store/auth';
import { useRouter } from 'vue-router'; // 添加router导入
import SaleForm from '../components/SaleForm.vue';

const salesStore = useSalesStore();
const authStore = useAuthStore();
const router = useRouter(); // 初始化router

// 状态变量
const showCreateForm = ref(false);
const showDetailModal = ref(false);
const currentSale = ref(null);
const filters = reactive({
  status: '',
  start_date: '',
  end_date: ''
});

// 权限检查
const hasRefundPermission = computed(() => {
  return authStore.isAdmin || authStore.hasPermission('manage_sales');
});

// 加载数据
onMounted(async () => {
  console.log('SalesView 组件挂载, 初始 isAuthenticated:', authStore.isAuthenticated);
  
  // 确保在执行任何操作前用户已认证
  if (!authStore.isAuthenticated) {
    console.log('SalesView: 用户未认证，将重定向到登录页面。');
    router.push('/login');
    return; // 阻止进一步执行
  }
  
  try {
    await loadSales();
  } catch (error) {
    console.error('加载销售数据失败 (onMounted catch):', error);
    // 如果 loadSales 抛出错误（包括可能的401），这里可以进一步处理
    // 但 loadSales 内部的错误处理应该已经处理了401
  }
});

// 加载销售记录
const loadSales = async () => {
  try {
    await salesStore.loadSales(filters);
  } catch (error) {
    console.error('加载销售记录失败 (loadSales function catch):', error);
    // 如果是认证错误，执行登出并重定向
    if (error.response && error.response.status === 401) {
      console.log('loadSales 中检测到 401 错误，执行登出。');
      authStore.logout(); // authStore.logout() 会处理重定向
    }
    throw error; 
  }
};

// 查看详情
const viewDetail = async (id) => {
  try {
    currentSale.value = await salesStore.getSale(id);
    showDetailModal.value = true;
  } catch (error) {
    console.error('获取销售详情失败:', error);
  }
};

// 关闭详情模态框
const closeDetailModal = () => {
  showDetailModal.value = false;
  currentSale.value = null;
};

// 处理退款
const handleRefund = async (id) => {
  if (!confirm('确认要为此销售记录办理退款吗？')) return;
  
  try {
    await salesStore.refundSale(id);
    // 刷新列表
    await salesStore.loadSales(filters);
  } catch (error) {
    console.error('退款处理失败:', error);
    alert('退款处理失败: ' + error.message);
  }
};

// 应用过滤器
const applyFilters = async () => {
  await salesStore.loadSales(filters);
};

// 分页
const changePage = async (page) => {
  await salesStore.loadSales({ ...filters, page });
};

// 处理新销售创建
const handleSaleCreated = async () => {
  showCreateForm.value = false;
  // 确保在加载销售数据前用户仍然是认证状态
  if (!authStore.isAuthenticated) {
    console.log('handleSaleCreated: 用户未认证，将重定向到登录页面。');
    router.push('/login');
    return;
  }
  await loadSales();
};

// 创建销售前检查用户登录状态
const checkBeforeCreateSale = () => {
  if (!authStore.isAuthenticated) {
    alert('您需要先登录才能创建销售记录');
    router.push('/login');
    return;
  }
  showCreateForm.value = true;
};

// 格式化日期
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

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'COMPLETED': '已完成',
    'REFUNDED': '已退款',
    'CANCELLED': '已取消'
  };
  return statusMap[status] || status;
};

// 获取支付方式文本
const getPaymentMethodText = (method) => {
  const methodMap = {
    'CASH': '现金',
    'CARD': '银行卡',
    'WECHAT': '微信支付',
    'ALIPAY': '支付宝'
  };
  return methodMap[method] || method;
};
</script>

<style scoped>
.sales-view {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h1 {
  margin: 0;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-section select,
.filter-section input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
}

.sales-table th,
.sales-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}

.sales-table th {
  background-color: #f2f2f2;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.completed {
  background-color: #dff0d8;
  color: #3c763d;
}

.refunded {
  background-color: #fcf8e3;
  color: #8a6d3b;
}

.cancelled {
  background-color: #f2dede;
  color: #a94442;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background-color: #337ab7;
  color: white;
}

.btn-info {
  background-color: #5bc0de;
  color: white;
}

.btn-warning {
  background-color: #f0ad4e;
  color: white;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #777;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.page-btn {
  padding: 5px 10px;
  border: none;
  background-color: #337ab7;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
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
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-lg {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.sale-info {
  margin-bottom: 20px;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
}

.info-row {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.info-item {
  flex: 1;
}

.info-item label {
  font-weight: bold;
  margin-right: 8px;
  color: #666;
}

.loading {
  text-align: center;
  padding: 30px;
  color: #777;
}
</style>

