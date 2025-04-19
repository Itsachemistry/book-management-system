<template>
  <div class="book-table-container">
    <!-- 加载状态显示 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div>加载中...</div>
    </div>
    
    <!-- 书籍表格 -->
    <table class="book-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>ISBN</th>
          <th>书名</th>
          <th>作者</th>
          <th>出版社</th>
          <th>售价</th>
          <th>库存</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id" :class="{ 'inactive-row': !book.is_active }">
          <td>{{ book.id }}</td>
          <td>{{ book.isbn }}</td>
          <td>{{ book.name }}</td>
          <td>{{ book.author || '-' }}</td>
          <td>{{ book.publisher || '-' }}</td>
          <td>¥{{ book.retail_price.toFixed(2) }}</td>
          <td>
            <span :class="{ 'low-stock': book.quantity < 10 }">
              {{ book.quantity }} 本
            </span>
          </td>
          <td>
            <div class="actions">
              <button 
                class="btn-edit" 
                @click="$emit('edit', book)"
                :disabled="!isAdmin"
                title="编辑"
              >
                编辑
              </button>
              <button 
                class="btn-delete" 
                @click="$emit('delete', book)"
                :disabled="!isAdmin"
                title="删除"
              >
                删除
              </button>
              <button 
                class="btn-view" 
                @click="$emit('view', book)"
                title="查看详情"
              >
                详情
              </button>
            </div>
          </td>
        </tr>
        <tr v-if="books.length === 0">
          <td colspan="8" class="empty-table">
            没有找到匹配的书籍
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 分页控件 -->
    <div class="pagination" v-if="pagination && pagination.pages > 1">
      <button 
        class="page-btn"
        @click="$emit('change-page', 1)"
        :disabled="pagination.page <= 1"
      >
        首页
      </button>
      <button 
        class="page-btn"
        @click="$emit('change-page', pagination.page - 1)"
        :disabled="pagination.page <= 1"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ pagination.page }} 页 / 共 {{ pagination.pages }} 页
      </span>
      <button 
        class="page-btn"
        @click="$emit('change-page', pagination.page + 1)"
        :disabled="pagination.page >= pagination.pages"
      >
        下一页
      </button>
      <button 
        class="page-btn"
        @click="$emit('change-page', pagination.pages)"
        :disabled="pagination.page >= pagination.pages"
      >
        末页
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

// 定义属性
const props = defineProps({
  books: {
    type: Array,
    required: true
  },
  pagination: {
    type: Object,
    default: () => ({
      page: 1,
      per_page: 20,
      total: 0,
      pages: 1
    })
  },
  loading: {
    type: Boolean,
    default: false
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
});

// 定义事件
const emit = defineEmits(['edit', 'delete', 'view', 'change-page']);
</script>

<style scoped>
.book-table-container {
  position: relative;
  width: 100%;
  overflow-x: auto;
}

.book-table {
  width: 100%;
  border-collapse: collapse;
}

.book-table th,
.book-table td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.book-table th {
  background-color: #f2f2f2;
  color: #333;
  font-weight: bold;
}

.book-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.book-table tr:hover {
  background-color: #f1f1f1;
}

.inactive-row {
  opacity: 0.6;
  background-color: #f8f8f8;
}

.low-stock {
  color: #e74c3c;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 5px;
}

.actions button {
  padding: 3px 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  color: white;
  font-size: 0.8rem;
}

.btn-edit {
  background-color: #3498db;
}

.btn-delete {
  background-color: #e74c3c;
}

.btn-view {
  background-color: #2ecc71;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.page-btn {
  padding: 5px 10px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.page-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.page-info {
  margin: 0 10px;
}

.empty-table {
  text-align: center;
  padding: 20px;
  color: #7f8c8d;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

