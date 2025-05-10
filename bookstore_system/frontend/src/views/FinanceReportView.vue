<template>
  <div class="finance-container">
    <h1>财务报表</h1>
    
    <!-- 筛选条件 -->
    <div class="filters">
      <div class="filter-section">
        <DateRangePicker 
          :startDate="filters.start_date"
          :endDate="filters.end_date"
          @change="handleDateChange"
        />
      </div>
      
      <div class="filter-section">
        <TransactionTypeFilter 
          :initialValue="filters.transaction_type || 'ALL'"
          @change="handleTypeFilterChange"
        />
      </div>
      
      <div class="filter-actions">
        <button class="btn btn-primary" @click="applyFilters">应用筛选</button>
        <button class="btn btn-secondary" @click="resetFilters">重置</button>
        <ExportButton 
          reportType="transactions" 
          :disabled="transactions.length === 0"
          @export="handleExport"
        />
      </div>
    </div>
    
    <!-- 财务摘要卡片 -->
    <FinanceSummaryCards 
      :income="summaryData.total_income"
      :expense="summaryData.total_expense"
      :profit="summaryData.net_profit"
      :compareData="periodComparisonData"
    />
    
    <!-- 数据可视化区域 -->
    <div class="charts-container">
      <div class="chart-wrapper trend-chart">
        <!-- 财务趋势图表 -->
        <FinanceTrendChart 
          :chart-data="trendChartData"
          :loading="loadingTrend"
          @period-change="handlePeriodChange"
        />
      </div>
      
      <div class="chart-wrapper pie-chart">
        <!-- 收支比例饼图 -->
        <FinancePieChart 
          title="收支分布"
          :chartData="pieChartData"
          :loading="loadingPieChart"
        />
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
import { ref, reactive, onMounted, computed } from 'vue';
import { getTransactions, getFinanceSummary, getFinanceTrend } from '../api/finance';
import { exportToCsv, exportToExcel, formatTransactionsForExport } from '../utils/reportExport';

// 导入所有组件
import DateRangePicker from '../components/DateRangePicker.vue';
import TransactionTypeFilter from '../components/TransactionTypeFilter.vue';
import FinanceSummaryCards from '../components/FinanceSummaryCards.vue';
import FinanceTrendChart from '../components/FinanceTrendChart.vue';
import FinancePieChart from '../components/FinancePieChart.vue';
import ExportButton from '../components/ExportButton.vue';

// 状态变量
const transactions = ref([]);
const summaryData = ref({
  total_income: 0,
  total_expense: 0,
  net_profit: 0,
  month_income: 0
});
const loading = ref(false);
const loadingTrend = ref(false);
const loadingPieChart = ref(false);
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

// 图表相关
const trendPeriod = ref('monthly');
const trendData = ref({
  dates: [],
  income: [],
  expense: [],
  profit: []
});

// 饼图数据
const pieChartData = ref([
  { name: '收入', value: 0 },
  { name: '支出', value: 0 }
]);

// 期间对比数据
const periodComparisonData = ref({
  income_change_rate: 0,
  expense_change_rate: 0,
  profit_change_rate: 0
});

// 计算属性：图表数据
const trendChartData = computed(() => {
  return {
    dates: trendData.value.dates || [],
    income: trendData.value.income || [],
    expense: trendData.value.expense || [],
    profit: trendData.value.profit || []
  };
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
  
  // 加载趋势数据
  loadTrendData();
  
  // 加载饼图数据
  loadPieChartData();
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
      transaction_type: filters.transaction_type === 'ALL' ? '' : filters.transaction_type,
      page: pagination.page,
      per_page: pagination.per_page
    };
    
    console.log('加载交易记录，参数:', params);
    
    const response = await getTransactions(params);
    transactions.value = response.transactions || [];
    
    // 调试信息
    console.log('获取到交易记录:', transactions.value);
    
    pagination.page = response.pagination?.page || 1;
    pagination.pages = response.pagination?.pages || 1;
    pagination.total = response.pagination?.total || 0;
  } catch (error) {
    console.error('加载交易记录失败:', error);
    transactions.value = [];
  }
};

// 加载财务摘要
const loadSummary = async () => {
  try {
    const params = {
      start_date: filters.start_date,
      end_date: filters.end_date
    };
    
    console.log('开始加载财务摘要，参数:', params);
    const response = await getFinanceSummary(params);
    console.log('获取到财务摘要数据:', response);
    
    summaryData.value = {
      total_income: response?.total_income || 0,
      total_expense: response?.total_expense || 0,
      net_profit: response?.net_profit || 0,
      month_income: response?.month_income || 0
    };
    
    // 同步饼图数据
    pieChartData.value = [
      { name: '收入', value: summaryData.value.total_income },
      { name: '支出', value: summaryData.value.total_expense }
    ];
    
    // 加载对比数据
    if (response?.comparison) {
      periodComparisonData.value = response.comparison;
    }
    
    console.log('财务摘要数据已更新:', summaryData.value);
  } catch (error) {
    console.error('加载财务摘要失败:', error);
    // 设置默认值确保界面不会崩溃
    summaryData.value = {
      total_income: 0,
      total_expense: 0,
      net_profit: 0,
      month_income: 0
    };
    pieChartData.value = [
      { name: '收入', value: 0 },
      { name: '支出', value: 0 }
    ];
  }
};

// 加载趋势数据
const loadTrendData = async () => {
  loadingTrend.value = true;
  try {
    const params = {
      period: trendPeriod.value,
      start_date: filters.start_date,
      end_date: filters.end_date,
      limit: 12 // 获取12个数据点
    };
    
    console.log('请求财务趋势数据，参数:', params);
    const response = await getFinanceTrend(params);
    console.log('接收到财务趋势数据:', response);
    
    if (!response || !Array.isArray(response)) {
      throw new Error('趋势数据格式不正确');
    }
    
    // 解析返回的数据，提取需要的字段
    const dates = response.map(item => item.period);
    const income = response.map(item => Number(item.income || 0));
    const expense = response.map(item => Number(item.expense || 0));
    const profit = response.map(item => Number(item.income || 0) - Number(item.expense || 0));
    
    trendData.value = {
      dates,
      income,
      expense,
      profit
    };
    
  } catch (error) {
    console.error('加载财务趋势数据失败:', error);
    trendData.value = {
      dates: [],
      income: [],
      expense: [],
      profit: []
    };
  } finally {
    loadingTrend.value = false;
  }
};

// 加载饼图数据
const loadPieChartData = async () => {
  loadingPieChart.value = true;
  try {
    // 使用已有的数据 (summaryData)
    pieChartData.value = [
      { name: '收入', value: Number(summaryData.value.total_income) || 0 },
      { name: '支出', value: Number(summaryData.value.total_expense) || 0 }
    ];
    console.log('饼图数据已更新:', pieChartData.value);
    // 检查数据是否为有效值
    console.log('数据是否有效:', 
      pieChartData.value[0].value !== 0 || pieChartData.value[1].value !== 0,
      '收入:', pieChartData.value[0].value,
      '支出:', pieChartData.value[1].value
    );
  } catch (error) {
    console.error('加载饼图数据失败:', error);
    pieChartData.value = [
      { name: '收入', value: 0 },
      { name: '支出', value: 0 }
    ];
  } finally {
    loadingPieChart.value = false;
  }
};

// 处理周期变化
const handlePeriodChange = (period) => {
  trendPeriod.value = period;
  loadTrendData();
};

// 处理日期变化
const handleDateChange = ({ startDate, endDate }) => {
  filters.start_date = startDate;
  filters.end_date = endDate;
};

// 处理交易类型过滤器变化
const handleTypeFilterChange = (type) => {
  filters.transaction_type = type;
};

// 应用筛选条件
const applyFilters = () => {
  pagination.page = 1;
  loadData();
  loadTrendData();
  loadPieChartData();
};

// 重置筛选条件
const resetFilters = () => {
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  
  filters.start_date = formatDateForInput(firstDay);
  filters.end_date = formatDateForInput(today);
  filters.transaction_type = 'ALL';
  
  pagination.page = 1;
  loadData();
  loadTrendData();
  loadPieChartData();
};

// 导出报表
const handleExport = async ({ format, reportType }) => {
  try {
    if (reportType === 'transactions' && transactions.value.length > 0) {
      // 获取完整的交易数据（所有页）
      let allTransactions = [];
      
      // 判断是否需要获取所有页面数据
      if (pagination.pages > 1 && pagination.total > transactions.value.length) {
        loading.value = true;
        // 如果数据超过一页，获取所有页的数据
        const params = {
          start_date: filters.start_date,
          end_date: filters.end_date,
          transaction_type: filters.transaction_type === 'ALL' ? '' : filters.transaction_type,
          per_page: pagination.total // 请求所有数据
        };
        
        try {
          const response = await getTransactions(params);
          allTransactions = response.transactions || [];
        } catch (error) {
          console.error('获取导出数据失败:', error);
          allTransactions = transactions.value;
        }
      } else {
        // 如果只有一页，使用当前数据
        allTransactions = transactions.value;
      }
      
      // 格式化交易记录为可导出格式
      const { data, columns } = formatTransactionsForExport(allTransactions);
      
      // 根据选择的格式导出
      const dateRange = filters.start_date && filters.end_date 
        ? `${filters.start_date}至${filters.end_date}`
        : '全部';
        
      const filename = `财务交易记录_${dateRange}`;
      
      if (format === 'csv') {
        exportToCsv(data, columns, filename);
      } else {
        exportToExcel(data, columns, filename, '财务交易记录');
      }
      
    } else {
      alert('暂无数据可导出');
    }
  } catch (error) {
    console.error('导出失败:', error);
    alert('导出失败: ' + error.message);
  } finally {
    loading.value = false;
  }
};

// 换页
const changePage = (page) => {
  pagination.page = page;
  loadTransactions();
};

// 格式化日期显示
const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // 如果无法解析为有效日期，返回原始字符串
    
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error('日期格式化失败:', error);
    return dateString;
  }
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
  flex-direction: column;
  gap: 15px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 10px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* 图表容器样式 */
.charts-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-wrapper {
  background-color: white;
  border-radius: 5px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
  padding: 15px;
}

.trend-chart {
  flex: 2;
  min-width: 500px;
}

.pie-chart {
  flex: 1;
  min-width: 300px;
}

.transactions-table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
  background: white;
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

/* 响应式布局 */
@media (max-width: 768px) {
  .charts-container {
    flex-direction: column;
  }
  
  .chart-wrapper {
    min-width: 100%;
  }
}
</style>

