<template>
  <div class="isbn-reference-view">
    <h1>ISBN引用查询</h1>
    
    <div class="search-box">
      <input 
        v-model="isbnQuery" 
        placeholder="请输入要查询的ISBN"
        class="form-control"
        @keyup.enter="searchIsbn"
      >
      <button 
        class="btn btn-primary" 
        @click="searchIsbn" 
        :disabled="loading || !isbnQuery.trim()"
      >
        {{ loading ? '查询中...' : '查询' }}
      </button>
    </div>
    
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <p>正在查询数据...</p>
    </div>
    
    <div v-if="references && !loading" class="references-container">
      <!-- 书籍基本信息 -->
      <div class="reference-section">
        <h2>书籍基本信息</h2>
        <table class="info-table">
          <tbody>
            <tr>
              <th>ISBN</th>
              <td>{{ references.book.isbn }}</td>
            </tr>
            <tr>
              <th>书名</th>
              <td>{{ references.book.name }}</td>
            </tr>
            <tr>
              <th>作者</th>
              <td>{{ references.book.author || '-' }}</td>
            </tr>
            <tr>
              <th>出版社</th>
              <td>{{ references.book.publisher || '-' }}</td>
            </tr>
            <tr>
              <th>零售价</th>
              <td>¥{{ references.book.retail_price }}</td>
            </tr>
            <tr>
              <th>库存</th>
              <td>{{ references.book.quantity }}</td>
            </tr>
            <tr>
              <th>状态</th>
              <td>{{ references.book.is_active ? '在售' : '已下架' }}</td>
            </tr>
            <tr>
              <th>创建时间</th>
              <td>{{ formatDate(references.book.created_at) }}</td>
            </tr>
            <tr>
              <th>更新时间</th>
              <td>{{ formatDate(references.book.updated_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 采购记录 -->
      <div class="reference-section">
        <h2>采购记录 ({{ references.purchase_items.length }})</h2>
        
        <div v-if="references.purchase_items.length === 0" class="no-data">
          该ISBN没有采购记录
        </div>
        
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>订单号</th>
              <th>供应商</th>
              <th>采购日期</th>
              <th>数量</th>
              <th>单价</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in references.purchase_items" :key="item.id">
              <td>{{ item.order_number }}</td>
              <td>{{ item.supplier || '-' }}</td>
              <td>{{ formatDate(item.order_date) }}</td>
              <td>{{ item.quantity }}</td>
              <td>¥{{ item.purchase_price }}</td>
              <td>
                <span :class="getStatusClass(item.order_status)">
                  {{ translateStatus(item.order_status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="actions">
        <button @click="goBack" class="btn btn-secondary">返回</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { getIsbnReferences } from '../api/books';

export default {
  name: 'IsbnReferenceView',
  
  setup() {
    const router = useRouter();
    const isbnQuery = ref('');
    const references = ref(null);
    const loading = ref(false);
    const error = ref(null);
    
    // 查询ISBN引用
    async function searchIsbn() {
      if (!isbnQuery.value.trim()) return;
      
      loading.value = true;
      error.value = null;
      references.value = null;
      
      try {
        references.value = await getIsbnReferences(isbnQuery.value.trim());
      } catch (err) {
        error.value = err.message || '查询失败，请稍后重试';
      } finally {
        loading.value = false;
      }
    }
    
    // 格式化日期
    function formatDate(dateString) {
      if (!dateString) return '-';
      
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
    
    // 订单状态翻译
    function translateStatus(status) {
      const statusMap = {
        'UNPAID': '未支付',
        'PAID': '已支付',
        'RETURNED': '已退货',
        'STOCKED': '已入库',
      };
      
      return statusMap[status] || status;
    }
    
    // 获取状态样式类
    function getStatusClass(status) {
      return `status-${status.toLowerCase()}`;
    }
    
    // 返回上一页
    function goBack() {
      router.back();
    }
    
    return {
      isbnQuery,
      references,
      loading,
      error,
      searchIsbn,
      formatDate,
      translateStatus,
      getStatusClass,
      goBack
    };
  }
};
</script>

<style scoped>
.isbn-reference-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #333;
}

.search-box {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.search-box input {
  flex-grow: 1;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
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

.btn:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
}

.references-container {
  margin-top: 30px;
}

.reference-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.reference-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  color: #333;
}

.info-table, .data-table {
  width: 100%;
  border-collapse: collapse;
}

.info-table th, .info-table td, 
.data-table th, .data-table td {
  padding: 12px;
  border: 1px solid #eee;
  text-align: left;
}

.info-table th {
  width: 150px;
  background-color: #f9f9f9;
}

.data-table th {
  background-color: #f9f9f9;
}

.data-table tr:hover {
  background-color: #f5f5f5;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 40px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert {
  padding: 12px 16px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.alert-danger {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #757575;
  font-style: italic;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.status-unpaid {
  color: #f57c00;
  font-weight: bold;
}

.status-paid {
  color: #0288d1;
  font-weight: bold;
}

.status-returned {
  color: #d32f2f;
  font-weight: bold;
}

.status-stocked {
  color: #388e3c;
  font-weight: bold;
}

.actions {
  margin-top: 20px;
  text-align: right;
}
</style>