<template>
  <div class="book-detail">
    <div class="detail-row">
      <div class="detail-label">ISBN:</div>
      <div class="detail-value">{{ book.isbn }}</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">书名:</div>
      <div class="detail-value">{{ book.name }}</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">作者:</div>
      <div class="detail-value">{{ book.author || '未知' }}</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">出版社:</div>
      <div class="detail-value">{{ book.publisher || '未知' }}</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">售价:</div>
      <div class="detail-value">¥{{ parseFloat(book.retail_price)?.toFixed(2) || '0.00' }}</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">库存:</div>
      <div class="detail-value">{{ book.quantity || 0 }} 本</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">状态:</div>
      <div class="detail-value">
        <span :class="book.is_active ? 'active-status' : 'inactive-status'">
          {{ book.is_active ? '有效' : '已下架' }}
        </span>
      </div>
    </div>
    <div class="detail-row">
      <div class="detail-label">创建时间:</div>
      <div class="detail-value">{{ formatDate(book.created_at) }}</div>
    </div>
    <div class="detail-row">
      <div class="detail-label">更新时间:</div>
      <div class="detail-value">{{ formatDate(book.updated_at) }}</div>
    </div>
    
    <div class="detail-actions">
      <button class="btn-close" @click="$emit('close')">关闭</button>
      <button 
        v-if="isAdmin" 
        class="btn-edit" 
        @click="$emit('edit')"
      >
        编辑
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  book: {
    type: Object,
    required: true
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'edit']);

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return '未知';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}
</script>

<style scoped>
.book-detail {
  padding: 15px;
}

.detail-row {
  display: flex;
  margin-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}

.detail-label {
  font-weight: bold;
  width: 100px;
  color: #555;
}

.detail-value {
  flex: 1;
}

.active-status {
  color: #2ecc71;
  font-weight: bold;
}

.inactive-status {
  color: #e74c3c;
  font-weight: bold;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-close {
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-edit {
  background-color: #f39c12;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-close:hover {
  background-color: #7f8c8d;
}

.btn-edit:hover {
  background-color: #e67e22;
}
</style>
