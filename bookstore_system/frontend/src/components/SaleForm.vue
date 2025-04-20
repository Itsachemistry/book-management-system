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
              <label for="book_select">选择书籍</label>
              <select id="book_select" v-model="selectedBook">
                <option value="">-- 选择一本书 --</option>
                <option v-for="book in availableBooks" :key="book.id" :value="book">
                  {{ book.name }} ({{ book.isbn }}) - ¥{{ book.retail_price.toFixed(2) }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="quantity">数量</label>
              <input
                type="number"
                id="quantity"
                v-model.number="quantity"
                min="1"
                max="100"
                :disabled="!selectedBook"
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
                <td>¥{{ item.price.toFixed(2) }}</td>
                <td>{{ item.quantity }}</td>
                <td>¥{{ calculateItemTotal(item).toFixed(2) }}</td>
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
import { ref, reactive, onMounted } from 'vue';
import { useBookStore } from '../store/book';
import { createSale } from '../api/sales';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['created', 'cancel']);

const bookStore = useBookStore();
const loading = ref(false);
const submitting = ref(false);
const selectedBook = ref(null);
const quantity = ref(1);

// 表单数据
const saleData = reactive({
  customer_name: '',
  contact: '',
  payment_method: 'CASH',
  remarks: '',
  items: []
});

// 可用书籍列表 (有库存的)
const availableBooks = ref([]);

// 加载书籍
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
      price: selectedBook.value.retail_price,
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
  return item.price * item.quantity;
};

// 计算总价
const calculateTotal = () => {
  return saleData.items.reduce((sum, item) => {
    return sum + calculateItemTotal(item);
  }, 0);
};

// 提交表单
const submitForm = async () => {
  if (saleData.items.length === 0) {
    alert('请至少添加一项商品');
    return;
  }
  
  submitting.value = true;
  
  try {
    // 准备提交数据
    const submitData = {
      customer_name: saleData.customer_name,
      contact: saleData.contact,
      payment_method: saleData.payment_method,
      remarks: saleData.remarks,
      items: saleData.items.map(item => ({
        book_id: item.book_id,
        quantity: item.quantity,
        price: item.price
      }))
    };
    
    const result = await createSale(submitData);
    emit('created', result);
  } catch (error) {
    console.error('创建销售失败:', error);
    alert('创建销售失败: ' + error.message);
  } finally {
    submitting.value = false;
  }
};

// 组件挂载时加载书籍
onMounted(() => {
  loadBooks();
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

.form-group textarea {
  resize: vertical;
}

.book-selection {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.book-selection .form-group {
  flex: 1;
  min-width: 200px;
}

.book-selection input[type="number"] {
  width: 100px;
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