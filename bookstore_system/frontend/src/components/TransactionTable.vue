<template>
  <div class="transaction-table-container">
    <!-- 加载状态显示 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>加载数据中...</p>
    </div>
    
    <!-- 无数据状态 -->
    <div v-else-if="!transactions || transactions.length === 0" class="no-data">
      <p>{{ noDataMessage }}</p>
    </div>
    
    <!-- 交易明细表格 -->
    <table v-else class="transaction-table">
      <thead>
        <tr>
          <th @click="sortBy('transaction_date')" class="sortable">
            日期 
            <span v-if="sortKey === 'transaction_date'" class="sort-icon">
              {{ sortOrder === 'asc' ? '▲' : '▼' }}
            </span>
          </th>
          <th @click="sortBy('type')" class="sortable">
            类型
            <span v-if="sortKey === 'type'" class="sort-icon">
              {{ sortOrder === 'asc' ? '▲' : '▼' }}
            </span>
          </th>
          <th>描述</th>
          <th @click="sortBy('amount')" class="sortable">
            金额
            <span v-if="sortKey === 'amount'" class="sort-icon">
              {{ sortOrder === 'asc' ? '▲' : '▼' }}
            </span>
          </th>
          <th>关联单据</th>
          <th>操作人</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="transaction in sortedTransactions" :key="transaction.id" :class="getRowClass(transaction)">
          <td>{{ formatDate(transaction.transaction_date) }}</td>
          <td>
            <span :class="getTypeBadgeClass(transaction)">
              {{ getTransactionTypeText(transaction.type) }}
            </span>
          </td>
          <td class="description-cell">{{ transaction.description || '无描述' }}</td>
          <td :class="getAmountClass(transaction)">
            {{ formatCurrency(transaction.amount) }}
          </td>
          <td>
            <span v-if="transaction.reference_id">
              {{ getReferenceTypeText(transaction.reference_type) }} #{{ transaction.reference_id }}
            </span>
            <span v-else>-</span>
          </td>
          <td>{{ transaction.user ? transaction.user.full_name || transaction.user.username : '未知' }}</td>
        </tr>
      </tbody>
    </table>
    
    <!-- 分页控件 -->
    <div v-if="showPagination && pagination.pages > 1" class="pagination">
      <button 
        class="page-btn"
        @click="changePage(1)"
        :disabled="pagination.page <= 1"
      >
        首页
      </button>
      <button 
        class="page-btn"
        @click="changePage(pagination.page - 1)"
        :disabled="pagination.page <= 1"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ pagination.page }} 页 / 共 {{ pagination.pages }} 页 (总计 {{ pagination.total }} 条记录)
      </span>
      <button 
        class="page-btn"
        @click="changePage(pagination.page + 1)"
        :disabled="pagination.page >= pagination.pages"
      >
        下一页
      </button>
      <button 
        class="page-btn"
        @click="changePage(pagination.pages)"
        :disabled="pagination.page >= pagination.pages"
      >
        末页
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';

// 定义组件接收的属性
const props = defineProps({
  transactions: {
    type: Array,
    default: () => []
  },
  pagination: {
    type: Object,
    default: () => ({ page: 1, per_page: 10, total: 0, pages: 1 })
  },
  loading: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  noDataMessage: {
    type: String,
    default: '没有找到交易记录'
  }
});

// 定义向父组件发出的事件
const emit = defineEmits(['change-page', 'sort']);

// 排序状态
const sortKey = ref('transaction_date');
const sortOrder = ref('desc');

// 处理分页变化
const changePage = (page) => {
  emit('change-page', page);
};

// 处理点击表头排序
const sortBy = (key) => {
  if (sortKey.value === key) {
    // 如果已经按此键排序，则切换排序顺序
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    // 否则按此键排序，默认降序
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
  
  // 通知父组件排序变化
  emit('sort', { key: sortKey.value, order: sortOrder.value });
};

// 排序后的交易数据
const sortedTransactions = computed(() => {
  if (!props.transactions || props.transactions.length === 0) {
    return [];
  }
  
  // 创建数据的副本以避免修改原始数据
  const sortedData = [...props.transactions];
  
  // 检查数据是否支持客户端排序
  // 如果分页数据已经在服务器端排序，则不需要再次排序
  if (!props.showPagination || props.pagination.total === props.transactions.length) {
    return sortData(sortedData);
  }
  
  return sortedData;
});

// 排序函数
const sortData = (data) => {
  return data.sort((a, b) => {
    let valueA, valueB;
    
    // 根据排序键获取要比较的值
    switch (sortKey.value) {
      case 'transaction_date':
        valueA = new Date(a.transaction_date);
        valueB = new Date(b.transaction_date);
        break;
      case 'amount':
        valueA = parseFloat(a.amount);
        valueB = parseFloat(b.amount);
        break;
      case 'type':
        valueA = a.type;
        valueB = b.type;
        break;
      default:
        valueA = a[sortKey.value];
        valueB = b[sortKey.value];
    }
    
    // 比较并返回排序结果
    if (valueA === valueB) {
      return 0;
    }
    
    const compareResult = valueA < valueB ? -1 : 1;
    return sortOrder.value === 'asc' ? compareResult : -compareResult;
  });
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// 格式化货币
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '¥0.00';
  
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value);
};

// 获取交易类型文本
const getTransactionTypeText = (type) => {
  const typeMap = {
    'INCOME': '收入',
    'EXPENSE': '支出'
  };
  return typeMap[type] || type;
};

// 获取引用类型文本
const getReferenceTypeText = (type) => {
  const typeMap = {
    'SALE': '销售单',
    'PURCHASE': '进货单',
    'SALE_REFUND': '销售退款',
    'PURCHASE_RETURN': '进货退货',
    'SALARY': '工资支出',
    'OTHER_INCOME': '其他收入',
    'OTHER_EXPENSE': '其他支出'
  };
  return typeMap[type] || type;
};

// 获取行样式类
const getRowClass = (transaction) => {
  return transaction.type === 'INCOME' ? 'income-row' : 'expense-row';
};

// 获取金额样式类
const getAmountClass = (transaction) => {
  return transaction.type === 'INCOME' ? 'income-amount' : 'expense-amount';
};

// 获取类型标签样式类
const getTypeBadgeClass = (transaction) => {
  return `type-badge ${transaction.type === 'INCOME' ? 'income-badge' : 'expense-badge'}`;
};
</script>

<style scoped>
.transaction-table-container {
  width: 100%;
  position: relative;
}

.transaction-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  background-color: white;
}

.transaction-table th,
.transaction-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
  text-align: left;
}

.transaction-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  position: sticky;
  top: 0;
  z-index: 1;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #e9ecef;
}

.sort-icon {
  margin-left: 5px;
  font-size: 0.8em;
}

.income-row {
  background-color: rgba(212, 237, 218, 0.1);
}

.expense-row {
  background-color: rgba(248, 215, 218, 0.1);
}

.income-amount {
  color: #28a745;
  font-weight: 600;
}

.expense-amount {
  color: #dc3545;
  font-weight: 600;
}

.description-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.income-badge {
  background-color: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.expense-badge {
  background-color: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.page-btn {
  padding: 6px 12px;
  background-color: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #e9ecef;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6c757d;
  font-size: 14px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 123, 255, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-data {
  padding: 40px 20px;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 4px;
}
</style>
