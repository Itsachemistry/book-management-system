<template>
  <div class="order-form">
    <form @submit.prevent="submitForm">
      <!-- 基本信息 -->
      <div class="form-section">
        <h3>基本信息</h3>
        <div class="form-row">
          <div class="form-group">
            <label for="supplier">供应商</label>
            <input
              type="text"
              id="supplier"
              v-model="orderData.supplier"
              class="form-control"
              placeholder="请输入供应商名称"
            />
          </div>
          
          <div class="form-group">
            <label for="remarks">备注</label>
            <textarea
              id="remarks"
              v-model="orderData.remarks"
              class="form-control"
              placeholder="可选：输入订单备注"
              rows="2"
            ></textarea>
          </div>
        </div>
      </div>
      
      <!-- 订单项 -->
      <div class="form-section">
        <h3>订单项目</h3>
        
        <div v-for="(item, index) in orderData.items" :key="index" class="order-item">
          <div class="order-item-header">
            <h4>项目 #{{ index + 1 }}</h4>
            <button 
              type="button" 
              class="btn btn-sm btn-danger" 
              v-if="orderData.items.length > 1"
              @click="removeItem(index)"
            >
              删除
            </button>
          </div>
          
          <div class="item-type-selector">
            <label>图书类型:</label>
            <div class="radio-group">
              <label>
                <input type="radio" v-model="item.isExistingBook" :value="true"> 选择已有图书
              </label>
              <label>
                <input type="radio" v-model="item.isExistingBook" :value="false"> 新图书
              </label>
            </div>
          </div>
          
          <!-- 已有图书 -->
          <div v-if="item.isExistingBook" class="existing-book-section">
            <div class="form-group">
              <label>选择图书</label>
              <select v-model="item.book_id" class="form-control" required>
                <option value="">-- 请选择图书 --</option>
                <option v-for="book in books" :key="book.id" :value="book.id">
                  {{ book.name }} ({{ book.isbn }}) - {{ book.author }}
                </option>
              </select>
            </div>
          </div>
          
          <!-- 新图书 -->
          <div v-else class="new-book-section">
            <div class="form-row">
              <div class="form-group">
                <label>ISBN</label>
                <input
                  type="text"
                  v-model="item.isbn"
                  class="form-control"
                  placeholder="请输入ISBN号码"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>书名</label>
                <input
                  type="text"
                  v-model="item.title"
                  class="form-control"
                  placeholder="请输入书名"
                  required
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>作者</label>
                <input
                  type="text"
                  v-model="item.author"
                  class="form-control"
                  placeholder="请输入作者"
                  required
                />
              </div>
              
              <div class="form-group">
                <label>出版社</label>
                <input
                  type="text"
                  v-model="item.publisher"
                  class="form-control"
                  placeholder="请输入出版社"
                  required
                />
              </div>
            </div>
          </div>
          
          <!-- 共有字段：数量和价格 -->
          <div class="form-row">
            <div class="form-group">
              <label>数量</label>
              <input
                type="number"
                v-model.number="item.quantity"
                class="form-control"
                min="1"
                required
              />
            </div>
            
            <div class="form-group">
              <label>进货单价(￥)</label>
              <input
                type="number"
                v-model.number="item.purchase_price"
                class="form-control"
                min="0.01"
                step="0.01"
                required
              />
            </div>
            
            <div class="form-group">
              <label>建议零售价(￥)</label>
              <input
                type="number"
                v-model.number="item.suggested_retail_price"
                class="form-control"
                min="0.01"
                step="0.01"
                placeholder="可选"
              />
            </div>
          </div>
          
          <div class="subtotal">
            小计: ￥{{ calculateSubtotal(item) }}
          </div>
        </div>
        
        <button type="button" class="btn btn-secondary" @click="addItem">
          + 添加项目
        </button>
      </div>
      
      <!-- 总计 -->
      <div class="order-total">
        <h3>订单总计: ￥{{ totalAmount }}</h3>
      </div>
      
      <!-- 提交按钮 -->
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
          取消
        </button>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? '提交中...' : '创建订单' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { useProcurementStore } from '../store/procurement';
import { getBooks } from '../api/books';

export default {
  name: 'OrderForm',
  emits: ['created', 'cancel'],
  
  setup(props, { emit }) {
    const procurementStore = useProcurementStore();
    
    // 状态变量
    const books = ref([]);
    const submitting = ref(false);
    
    // 订单数据
    const orderData = reactive({
      supplier: '',
      remarks: '',
      items: [createEmptyItem()]
    });
    
    // 获取图书列表
    const loadBooks = async () => {
      try {
        const response = await getBooks();
        books.value = response.books;
      } catch (error) {
        console.error('Failed to load books:', error);
      }
    };
    
    // 创建空的订单项
    function createEmptyItem() {
      return {
        isExistingBook: true,
        book_id: '',
        isbn: '',
        title: '',
        author: '',
        publisher: '',
        quantity: 1,
        purchase_price: 0,
        suggested_retail_price: null
      };
    }
    
    // 添加订单项
    const addItem = () => {
      orderData.items.push(createEmptyItem());
    };
    
    // 移除订单项
    const removeItem = (index) => {
      orderData.items.splice(index, 1);
    };
    
    // 计算小计
    const calculateSubtotal = (item) => {
      return (item.quantity * item.purchase_price).toFixed(2);
    };
    
    // 计算总金额
    const totalAmount = computed(() => {
      return orderData.items.reduce((sum, item) => {
        return sum + (item.quantity * item.purchase_price);
      }, 0).toFixed(2);
    });
    
    // 提交表单
    const submitForm = async () => {
      if (orderData.items.length === 0) {
        alert('请至少添加一个订单项');
        return;
      }
      
      // 表单验证
      for (const item of orderData.items) {
        if (item.isExistingBook) {
          if (!item.book_id) {
            alert('请选择已有图书');
            return;
          }
        } else {
          if (!item.isbn || !item.title || !item.author || !item.publisher) {
            alert('请填写完整的新图书信息');
            return;
          }
        }
        
        if (item.quantity <= 0) {
          alert('图书数量必须大于0');
          return;
        }
        
        if (item.purchase_price <= 0) {
          alert('进货单价必须大于0');
          return;
        }
      }
      
      submitting.value = true;
      
      try {
        // 转换为API所需格式
        const payload = {
          supplier: orderData.supplier,
          remarks: orderData.remarks,
          items: orderData.items.map(item => {
            const result = {
              quantity: item.quantity,
              purchase_price: item.purchase_price,
              suggested_retail_price: item.suggested_retail_price || null
            };
            
            if (item.isExistingBook) {
              result.book_id = item.book_id;
            } else {
              result.isbn = item.isbn;
              result.title = item.title;
              result.author = item.author;
              result.publisher = item.publisher;
            }
            
            return result;
          })
        };
        
        const newOrder = await procurementStore.addOrder(payload);
        emit('created', newOrder);
      } catch (error) {
        console.error('Failed to create order:', error);
        alert('创建订单失败: ' + error.message);
      } finally {
        submitting.value = false;
      }
    };
    
    // 加载图书数据
    onMounted(() => {
      loadBooks();
    });
    
    return {
      books,
      orderData,
      submitting,
      addItem,
      removeItem,
      calculateSubtotal,
      totalAmount,
      submitForm
    };
  }
};
</script>

<style scoped>
.order-form {
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

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  flex: 1;
  min-width: 0;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

textarea.form-control {
  resize: vertical;
}

.order-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px dashed #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.order-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.order-item-header h4 {
  margin: 0;
  font-size: 16px;
}

.item-type-selector {
  margin-bottom: 15px;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin-top: 5px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.existing-book-section,
.new-book-section {
  border-top: 1px solid #eee;
  padding-top: 15px;
  margin-bottom: 15px;
}

.subtotal {
  margin-top: 10px;
  text-align: right;
  font-weight: bold;
  font-size: 16px;
}

.order-total {
  text-align: right;
  margin: 20px 0;
  font-size: 18px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
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

.btn-danger {
  background-color: #e53935;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>