<template>
  <div class="finance-container">
    <h1>财务报表</h1>
    
    <!-- 筛选条件 -->
    <div class="filters">
      <div class="filter-group">
        <label>日期范围：</label>
        <input 
          type="date" 
          v-model="filters.start_date" 
          class="date-input" 
        />
        <span>至</span>
        <input 
          type="date" 
          v-model="filters.end_date" 
          class="date-input" 
        />
      </div>
      
      <div class="filter-group">
        <label>交易类型：</label>
        <select v-model="filters.transaction_type">
          <option value="">全部</option>
          <option value="INCOME">收入</option>
          <option value="EXPENSE">支出</option>
        </select>
      </div>
      
      <button class="btn btn-primary" @click="applyFilters">应用筛选</button>
      <button class="btn btn-secondary" @click="resetFilters">重置</button>
    </div>
    
    <!-- 财务摘要 -->
    <div class="summary">
      <div class="summary-card income">
        <div class="summary-title">总收入</div>
        <div class="summary-value">¥{{ summaryData.total_income.toFixed(2) }}</div>
      </div>
      
      <div class="summary-card expense">
        <div class="summary-title">总支出</div>
        <div class="summary-value">¥{{ summaryData.total_expense.toFixed(2) }}</div>
      </div>
      
      <div class="summary-card profit">
        <div class="summary-title">净利润</div>
        <div class="summary-value">¥{{ summaryData.net_profit.toFixed(2) }}</div>
      </div>
    </div>
    
    <!-- 交易记录 -->
    <div class="transactions-section">
      <h2>交易记录</h2>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <table v-else class="transactions-table">
        <thead>
          <tr>
            <th>日期</th>
            <th>交易类型</th>
            <th>金额</th>
            <th>描述</th>
            <th>参考订单</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="transaction in transactions" :key="transaction.id" :class="transaction.transaction_type.toLowerCase()">
            <td>{{ formatDate(transaction.date) }}</td>
            <td>
              <span class="type-badge" :class="transaction.transaction_type.toLowerCase()">
                {{ getTransactionTypeText(transaction.transaction_type) }}
              </span>
            </td>
            <td>¥{{ parseFloat(transaction.amount).toFixed(2) }}</td>
            <td>{{ transaction.description }}</td>
            <td>{{ transaction.reference_number }}</td>
          </tr>
          <tr v-if="transactions.length === 0">
            <td colspan="5" class="no-data">暂无交易记录</td>
          </tr>
        </tbody>
      </table>
      
      <!-- 分页 -->
      <div v-if="pagination.pages > 1" class="pagination">
        <button 
          class="btn page-btn" 
          @click="changePage(pagination.page - 1)"
          :disabled="pagination.page <= 1"
        >
          上一页
        </button>
        <span class="page-info">
          {{ pagination.page }} / {{ pagination.pages }}
        </span>
        <button 
          class="btn page-btn" 
          @click="changePage(pagination.page + 1)"
          :disabled="pagination.page >= pagination.pages"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { getTransactions, getFinanceSummary } from '../api/finance';

// 状态变量
const transactions = ref([]);
const summaryData = ref({
  total_income: 0,
  total_expense: 0,
  net_profit: 0
});
const loading = ref(false);
const filters = reactive({
  start_date: '',
  end_date: '',
  transaction_type: ''
});
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 1
});

// 初始化
onMounted(() => {
  // 默认设置为本月范围
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  
  filters.start_date = formatDateForInput(firstDay);
  filters.end_date = formatDateForInput(today);
  
  // 加载数据
  loadData();
});

// 加载交易数据和财务摘要
const loadData = async () => {
  loading.value = true;
  
  try {
    // 加载交易记录
    await loadTransactions();
    
    // 加载财务摘要
    await loadSummary();
  } catch (error) {
    console.error('加载财务数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 加载交易记录
const loadTransactions = async () => {
  try {
    const params = {
      start_date: filters.start_date,
      end_date: filters.end_date,
      transaction_type: filters.transaction_type,
      page: pagination.page,
      per_page: pagination.per_page
    };
    
    const response = await getTransactions(params);
    transactions.value = response.transactions;
    pagination.page = response.pagination.page;
    pagination.pages = response.pagination.pages;
    pagination.total = response.pagination.total;
  } catch (error) {
    console.error('加载交易记录失败:', error);
  }
};

// 加载财务摘要
const loadSummary = async () => {
  try {
    const params = {
      start_date: filters.start_date,
      end_date: filters.end_date
    };
    
    const response = await getFinanceSummary(params);
    summaryData.value = response;
  } catch (error) {
    console.error('加载财务摘要失败:', error);
  }
};

// 应用筛选条件
const applyFilters = () => {
  pagination.page = 1;
  loadData();
};

// 重置筛选条件
const resetFilters = () => {
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  
  filters.start_date = formatDateForInput(firstDay);
  filters.end_date = formatDateForInput(today);
  filters.transaction_type = '';
  
  pagination.page = 1;
  loadData();
};

// 换页
const changePage = (page) => {
  pagination.page = page;
  loadTransactions();
};

// 格式化日期显示
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

// 格式化日期为input标签值
const formatDateForInput = (date) => {
  return date.toISOString().split('T')[0];
};

// 获取交易类型文本
const getTransactionTypeText = (type) => {
  const typeMap = {
    'INCOME': '收入',
    'EXPENSE': '支出'
  };
  return typeMap[type] || type;
};
</script>

<style scoped>
.finance-container {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

h2 {
  margin-top: 30px;
  margin-bottom: 15px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.summary {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  flex: 1;
  padding: 20px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-card.income {
  background-color: #d4edda;
  color: #155724;
}

.summary-card.expense {
  background-color: #f8d7da;
  color: #721c24;
}

.summary-card.profit {
  background-color: #cce5ff;
  color: #004085;
}

.summary-title {
  font-size: 16px;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
}

.transactions-table {
  width: 100%;
  border-collapse: collapse;
}

.transactions-table th,
.transactions-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}

.transactions-table th {
  background-color: #f2f2f2;
}

.income {
  background-color: rgba(212, 237, 218, 0.3);
}

.expense {
  background-color: rgba(248, 215, 218, 0.3);
}

.type-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.type-badge.income {
  background-color: #d4edda;
  color: #155724;
}

.type-badge.expense {
  background-color: #f8d7da;
  color: #721c24;
}

.loading {
  text-align: center;
  padding: 30px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.page-info {
  color: #666;
}

.page-btn {
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
}

.page-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>

