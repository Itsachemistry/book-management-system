<template>
  <div class="sale-form-container">
    <form @submit.prevent="submitForm">
      <div class="form-section">
        <h3>客户信息</h3>
        <div class="form-group">
          <label for="customer_name">客户名称</label>
          <input
            type="text"
            id="customer_name"
            v-model="saleData.customer_name"
            placeholder="输入客户名称（可选）"
          />
        </div>
        
        <div class="form-group">
          <label for="contact">联系方式</label>
          <input
            type="text"
            id="contact"
            v-model="saleData.contact"
            placeholder="联系方式（可选）"
          />
        </div>
      </div>
      
      <div class="form-section">
        <h3>商品信息</h3>
        <div v-if="loading" class="loading">
          <p>加载书籍中...</p>
        </div>
        <div v-else>
          <div class="book-selection">
            <div class="form-group">
              <label for="book_search">搜索书籍 (书名或ISBN)</label>
              <div class="search-container">
                <input
                  type="text"
                  id="book_search"
                  v-model="searchQuery"
                  @input="searchBooks"
                  placeholder="输入书名或ISBN"
                  autocomplete="off"
                />
                <div v-if="isSearching" class="search-loader">搜索中...</div>
              </div>
              
              <!-- 搜索结果下拉框 -->
              <div v-if="showResults && searchResults.length > 0" class="search-results">
                <div 
                  v-for="book in searchResults" 
                  :key="book.id" 
                  class="search-result-item"
                  :class="{'exact-match': book.exactMatch}"
                  @click="selectBook(book)"
                >
                  <div class="book-title">
                    {{ book.name }}
                    <span v-if="book.exactMatch" class="match-badge">精确匹配</span>
                  </div>
                  <div class="book-details">
                    ISBN: {{ book.isbn }} | 作者: {{ book.author || '未知' }} | 库存: {{ book.quantity }} | 价格: ¥{{ parseFloat(book.retail_price).toFixed(2) }}
                  </div>
                </div>
              </div>
              <div v-else-if="showResults && searchQuery && !isSearching" class="no-results">
                未找到匹配的图书
              </div>
            </div>
            
            <div v-if="selectedBook" class="selected-book">
              <span>已选：《{{ selectedBook.name }}》 - 库存: {{ selectedBook.quantity }}</span>
              <div class="quantity-input">
                <label for="quantity">数量:</label>
                <input
                  type="number"
                  id="quantity"
                  v-model.number="quantity"
                  min="1"
                  :max="selectedBook.quantity"
                  required
                />
              </div>
              
              <button 
                type="button" 
                class="btn btn-add-item" 
                @click="addItem"
                :disabled="!selectedBook || quantity < 1"
              >
                添加到购物车
              </button>
            </div>
          </div>
        </div>
        
        <!-- 购物车 -->
        <div class="shopping-cart">
          <h4>购物车</h4>
          <div v-if="saleData.items.length === 0" class="empty-cart">
            购物车为空
          </div>
          <table v-else class="cart-table">
            <thead>
              <tr>
                <th>书名</th>
                <th>单价</th>
                <th>数量</th>
                <th>小计</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in saleData.items" :key="index">
                <td>{{ item.book.name }}</td>
                <td>¥{{ parseFloat(item.price).toFixed(2) }}</td>
                <td>{{ item.quantity }}</td>
                <td>¥{{ parseFloat(calculateItemTotal(item)).toFixed(2) }}</td>
                <td>
                  <button 
                    type="button" 
                    class="btn btn-remove" 
                    @click="removeItem(index)"
                  >
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="3" class="total-label">总计:</td>
                <td colspan="2" class="total-amount">¥{{ calculateTotal().toFixed(2) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      
      <div class="form-section">
        <h3>支付信息</h3>
        <div class="form-group">
          <label for="payment_method">支付方式</label>
          <select id="payment_method" v-model="saleData.payment_method">
            <option value="CASH">现金</option>
            <option value="CARD">银行卡</option>
            <option value="WECHAT">微信支付</option>
            <option value="ALIPAY">支付宝</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="remarks">备注</label>
          <textarea
            id="remarks"
            v-model="saleData.remarks"
            rows="2"
            placeholder="备注信息（可选）"
          ></textarea>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="$emit('cancel')">
          取消
        </button>
        <button 
          type="submit" 
          class="btn btn-submit" 
          :disabled="submitting || saleData.items.length === 0"
        >
          {{ submitting ? '处理中...' : '完成销售' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { useBookStore } from '../store/book';
import { useSalesStore } from '../store/sales';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['created', 'cancel']);

const bookStore = useBookStore();
const salesStore = useSalesStore();
const loading = ref(false);
const submitting = ref(false);
const selectedBook = ref(null);
const quantity = ref(1);
const searchQuery = ref('');
const searchResults = ref([]);
const isSearching = ref(false);
const showResults = ref(false);
const availableBooks = ref([]);

// 表单数据
const saleData = reactive({
  customer_name: '',
  contact: '',
  payment_method: 'CASH',
  remarks: '',
  items: []
});

// 修改为使用防抖函数处理搜索
const debouncedSearch = (() => {
  let timeout;
  return (query) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      if (query && query.length >= 1) { // 降低触发字符数到1
        searchBooks(query);
      } else {
        searchResults.value = [];
        showResults.value = false;
      }
    }, 300); // 300ms防抖延迟
  };
})();

// 监听搜索输入
watch(searchQuery, (newValue) => {
  debouncedSearch(newValue);
});

// 搜索图书 - 修改搜索逻辑
const searchBooks = async (query) => {
  isSearching.value = true;
  showResults.value = true;
  
  try {
    // 判断是否可能是ISBN (纯数字或带连字符的数字字符串)
    const isIsbnLike = /^[0-9\-]+$/.test(query);
    
    // 1. 对于ISBN格式的查询，降低搜索字符门槛
    const minLength = isIsbnLike ? 1 : 2;
    
    if (query.length < minLength) {
      searchResults.value = [];
      return;
    }
    
    // 2. 执行模糊搜索
    await bookStore.loadBooks({
      search: query,
      active_only: true,
      per_page: 10
    });
    
    // 3. 只显示有库存的书籍
    searchResults.value = bookStore.books.filter(book => book.quantity > 0);
    
    // 4. 对于类似ISBN的长查询，尝试精确查找
    if (isIsbnLike && query.length >= 8) {
      try {
        const book = await bookStore.loadBookByIsbn(query);
        if (book && book.quantity > 0) {
          const existingIndex = searchResults.value.findIndex(b => b.id === book.id);
          if (existingIndex !== -1) {
            searchResults.value.splice(existingIndex, 1);
          }
          book.exactMatch = true;
          searchResults.value.unshift(book);
        }
      } catch (error) {
        console.log('ISBN精确查询未找到结果:', error);
      }
    }
  } catch (error) {
    console.error('搜索图书失败:', error);
    searchResults.value = [];
  } finally {
    isSearching.value = false;
  }
};

// 选择图书
const selectBook = (book) => {
  selectedBook.value = book;
  quantity.value = 1;
  searchQuery.value = '';
  showResults.value = false;
};

// 添加购物项
const addItem = () => {
  if (!selectedBook.value || quantity.value < 1) return;
  
  // 检查库存
  if (quantity.value > selectedBook.value.quantity) {
    alert(`库存不足! 当前库存: ${selectedBook.value.quantity}`);
    return;
  }
  
  // 检查是否已添加过该书籍
  const existingIndex = saleData.items.findIndex(item => 
    item.book.id === selectedBook.value.id
  );
  
  if (existingIndex >= 0) {
    // 更新数量
    saleData.items[existingIndex].quantity += quantity.value;
  } else {
    // 添加新项
    saleData.items.push({
      book_id: selectedBook.value.id,
      book: selectedBook.value,
      price: parseFloat(selectedBook.value.retail_price),
      quantity: quantity.value
    });
  }
  
  // 重置选择
  selectedBook.value = null;
  quantity.value = 1;
};

// 删除购物项
const removeItem = (index) => {
  saleData.items.splice(index, 1);
};

// 计算单项总价
const calculateItemTotal = (item) => {
  return parseFloat(item.price) * item.quantity;
};

// 计算总价
const calculateTotal = () => {
  return saleData.items.reduce((sum, item) => {
    return sum + parseFloat(calculateItemTotal(item));
  }, 0);
};

// 加载书籍列表
const loadBooks = async () => {
  loading.value = true;
  try {
    await bookStore.loadBooks({ active_only: true, per_page: 100 });
    // 过滤有库存的书籍
    availableBooks.value = bookStore.books.filter(book => book.quantity > 0);
  } catch (error) {
    console.error('加载书籍失败:', error);
  } finally {
    loading.value = false;
  }
};

// 提交表单
const submitForm = async () => {
  if (saleData.items.length === 0) {
    alert('请至少添加一项商品');
    return;
  }
  
  submitting.value = true;
  
  try {
    // 检查登录状态
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.error('提交表单时发现未登录状态');
      alert('您的登录状态已失效，请重新登录后再试');
      submitting.value = false;
      return;
    }
    
    // 准备提交数据
    const submitData = {
      customer_name: saleData.customer_name || null,
      contact: saleData.contact || null,
      payment_method: saleData.payment_method || 'CASH',
      remarks: saleData.remarks || null,
      items: saleData.items.map(item => ({
        book_id: Number(item.book_id),
        quantity: Number(item.quantity),
        price: parseFloat(item.price)
      }))
    };
    
    // 使用 store 进行调用
    const result = await salesStore.createSale(submitData);
    emit('created', result);
  } catch (error) {
    console.error('创建销售失败:', error);
    if (error.message.includes('会话已过期')) {
      alert('您的登录状态已失效，请重新登录后再试');
    } else if (error.response && error.response.data && error.response.data.error) {
      alert('创建销售失败: ' + error.response.data.error);
    } else {
      alert('创建销售失败: ' + (error.message || '未知错误'));
    }
  } finally {
    submitting.value = false;
  }
};

// 点击外部关闭搜索结果
const handleClickOutside = (e) => {
  if (!e.target.closest('.search-container') && !e.target.closest('.search-results')) {
    showResults.value = false;
  }
};

// 组件挂载时加载书籍
onMounted(() => {
  loadBooks();
  document.addEventListener('click', handleClickOutside);
});

// 在组件卸载时移除事件监听器
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

// 组件卸载时清理资源
onMounted(() => {
  return () => {
    document.removeEventListener('click', handleClickOutside);
  };
});
</script>

<style scoped>
.sale-form-container {
  max-width: 100%;
}

.form-section {
  margin-bottom: 25px;
  border: 1px solid #eee;
  border-radius: 5px;
  padding: 15px;
  background-color: #fdfdfd;
}

h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 16px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-container {
  position: relative;
}

.search-loader {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #666;
}

.search-results {
  position: absolute;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.search-result-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.search-result-item:hover {
  background-color: #f5f5f5;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item.exact-match {
  background-color: #e6f7ff;
}

.book-title {
  font-weight: bold;
  margin-bottom: 3px;
}

.book-title .match-badge {
  display: inline-block;
  margin-left: 5px;
  padding: 2px 6px;
  font-size: 12px;
  color: white;
  background-color: #007bff;
  border-radius: 3px;
}

.book-details {
  font-size: 12px;
  color: #666;
}

.no-results {
  padding: 10px;
  color: #666;
  text-align: center;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.selected-book {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.quantity-input {
  display: flex;
  align-items: center;
  gap: 5px;
}

.quantity-input input {
  width: 60px;
}

.form-group textarea {
  resize: vertical;
}

.book-selection {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cart-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.cart-table th,
.cart-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.cart-table th {
  background-color: #f5f5f5;
}

.total-label {
  text-align: right;
  font-weight: bold;
}

.total-amount {
  font-weight: bold;
  font-size: 16px;
}

.empty-cart {
  padding: 15px;
  text-align: center;
  color: #777;
  border: 1px dashed #ddd;
  margin-top: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-add-item {
  background-color: #28a745;
  color: white;
}

.btn-add-item:hover {
  background-color: #218838;
}

.btn-add-item:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-remove {
  background-color: #dc3545;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.btn-remove:hover {
  background-color: #c82333;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-submit {
  background-color: #007bff;
  color: white;
}

.btn-submit:hover {
  background-color: #0069d9;
}

.btn-submit:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #777;
}
</style>