<template>
  <form @submit.prevent="handleSubmit" class="book-form">
    <div class="form-group">
      <label for="isbn">ISBN <span class="required">*</span></label>
      <input
        type="text"
        id="isbn"
        v-model="form.isbn"
        :disabled="isEditMode || loading"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="name">书名 <span class="required">*</span></label>
      <input
        type="text"
        id="name"
        v-model="form.name"
        :disabled="loading"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="author">作者</label>
      <input
        type="text"
        id="author"
        v-model="form.author"
        :disabled="loading"
      />
    </div>
    
    <div class="form-group">
      <label for="publisher">出版社</label>
      <input
        type="text"
        id="publisher"
        v-model="form.publisher"
        :disabled="loading"
      />
    </div>
    
    <div class="form-group">
      <label for="retail_price">售价 <span class="required">*</span></label>
      <input
        type="number"
        id="retail_price"
        v-model.number="form.retail_price"
        step="0.01"
        min="0"
        :disabled="loading"
        required
      />
    </div>
    
    <div class="form-group">
      <label for="quantity">库存数量 <span class="required">*</span></label>
      <input
        type="number"
        id="quantity"
        v-model.number="form.quantity"
        step="1"
        min="0"
        :disabled="loading"
        required
      />
    </div>
    
    <div v-if="isEditMode" class="form-group">
      <label>
        <input
          type="checkbox"
          v-model="form.is_active"
          :disabled="loading"
        />
        图书有效（取消勾选表示下架）
      </label>
    </div>
    
    <div class="form-actions">
      <button 
        type="button" 
        class="btn-cancel" 
        @click="$emit('cancel')"
        :disabled="loading"
      >
        取消
      </button>
      <button 
        type="submit" 
        class="btn-submit" 
        :disabled="loading"
      >
        {{ submitText }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue';

// 定义属性
const props = defineProps({
  book: {
    type: Object,
    default: () => ({
      isbn: '',
      name: '',
      author: '',
      publisher: '',
      retail_price: 0,
      quantity: 0,
      is_active: true
    })
  },
  isEditMode: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
});

// 定义事件
const emit = defineEmits(['save', 'cancel']);

// 表单状态
const form = ref({
  isbn: '',
  name: '',
  author: '',
  publisher: '',
  retail_price: 0,
  quantity: 0,
  is_active: true
});

// 计算属性：提交按钮文本
const submitText = props.isEditMode 
  ? props.loading ? '保存中...' : '保存修改'
  : props.loading ? '添加中...' : '添加书籍';

// 当book属性变化时，更新表单
watch(() => props.book, (newVal) => {
  if (newVal) {
    form.value = { ...newVal };
  }
}, { deep: true, immediate: true });

// 提交表单
function handleSubmit() {
  // 创建一个新对象，避免直接修改表单状态
  const bookData = { 
    isbn: form.value.isbn,
    name: form.value.name,
    author: form.value.author || '',
    publisher: form.value.publisher || '',
    // 确保价格和数量是数字类型
    retail_price: parseFloat(form.value.retail_price),
    quantity: parseInt(form.value.quantity, 10)
  };
  
  // 如果是编辑模式，添加is_active字段
  if (props.isEditMode) {
    bookData.is_active = form.value.is_active;
  }
  
  console.log('提交书籍数据：', bookData);
  
  // 调用父组件的保存方法
  emit('save', bookData);
}
</script>

<style scoped>
.book-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #e74c3c;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-submit {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-cancel {
  background-color: #95a5a6;
  color: white;
}

.btn-submit {
  background-color: #3498db;
  color: white;
}

.btn-cancel:hover {
  background-color: #7f8c8d;
}

.btn-submit:hover {
  background-color: #2980b9;
}

button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}
</style>