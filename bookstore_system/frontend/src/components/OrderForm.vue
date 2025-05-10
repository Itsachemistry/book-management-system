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
          
          <!-- 统一的图书信息输入表单 -->
          <div class="book-form">
            <div class="form-group">
              <label>ISBN <span class="required">*</span></label>
              <div class="isbn-input-group">
                <input
                  type="text"
                  v-model="item.isbn"
                  class="form-control"
                  placeholder="输入ISBN"
                  required
                  @blur="checkIsbnExists(item)"
                />
                <button 
                  type="button" 
                  class="btn btn-sm btn-secondary" 
                  @click="checkIsbnExists(item)"
                >
                  查询
                </button>
              </div>
              <div v-if="item.isExistingBook" class="book-exists-notice">
                此图书已存在，信息已自动填充
              </div>
            </div>
            
            <div class="form-group">
              <label>书名 <span class="required">*</span></label>
              <input
                type="text"
                v-model="item.title"
                class="form-control"
                placeholder="图书标题"
                required
              />
            </div>
            
            <div class="form-group">
              <label>作者</label>
              <input
                type="text"
                v-model="item.author"
                class="form-control"
                placeholder="作者"
              />
            </div>
            
            <div class="form-group">
              <label>出版社</label>
              <input
                type="text"
                v-model="item.publisher"
                class="form-control"
                placeholder="出版社"
              />
            </div>
            
            <div class="form-group">
              <label>数量 <span class="required">*</span></label>
              <input
                type="number"
                v-model.number="item.quantity"
                class="form-control"
                min="1"
                required
              />
            </div>
            
            <div class="form-group">
              <label>进货单价(￥) <span class="required">*</span></label>
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
import { getBooks, getBookByIsbn } from '../api/books';

export default {
  name: 'OrderForm',
  emits: ['created', 'cancel'],
  
  setup(props, { emit }) {
    const procurementStore = useProcurementStore();
    
    // 状态变量
    const submitting = ref(false);
    const error = ref(null);
    
    // 订单数据
    const orderData = reactive({
      supplier: '',
      remarks: '',
      items: [createNewItem()]
    });
    
    // 创建新的订单项
    function createNewItem() {
      return {
        isbn: '',
        title: '',
        author: '',
        publisher: '',
        quantity: 1,
        purchase_price: 0,
        suggested_retail_price: null,
        isExistingBook: false,
        book_id: null
      };
    }
    
    // 添加订单项
    function addItem() {
      orderData.items.push(createNewItem());
    }
    
    // 移除订单项
    function removeItem(index) {
      orderData.items.splice(index, 1);
    }
    
    // 检查ISBN是否存在于数据库中
    async function checkIsbnExists(item) {
      if (!item.isbn) return;
      
      try {
        const book = await getBookByIsbn(item.isbn);
        
        if (book) {
          // 图书存在，自动填充信息
          item.isExistingBook = true;
          item.book_id = book.id;
          item.title = book.name;
          item.author = book.author || '';
          item.publisher = book.publisher || '';
          
          // 如果零售价未设置，可以参考原有的零售价
          if (!item.suggested_retail_price && book.retail_price) {
            item.suggested_retail_price = book.retail_price;
          }
        } else {
          // 图书不存在，重置为新图书
          item.isExistingBook = false;
          item.book_id = null;
        }
      } catch (err) {
        console.error('检查ISBN失败:', err);
        item.isExistingBook = false;
        item.book_id = null;
      }
    }
    
    // 计算小计
    function calculateSubtotal(item) {
      return ((item.quantity || 0) * (item.purchase_price || 0)).toFixed(2);
    }
    
    // 计算总金额
    const totalAmount = computed(() => {
      return orderData.items.reduce((sum, item) => {
        return sum + (item.quantity || 0) * (item.purchase_price || 0);
      }, 0).toFixed(2);
    });
    
    // 提交表单
    async function submitForm() {
      submitting.value = true;
      error.value = null;
      
      try {
        // 转换数据格式
        const orderPayload = {
          supplier: orderData.supplier,
          remarks: orderData.remarks,
          items: orderData.items.map(item => ({
            book_id: item.book_id,
            isbn: item.isbn,
            title: item.title,
            author: item.author,
            publisher: item.publisher,
            quantity: item.quantity,
            purchase_price: item.purchase_price,
            suggested_retail_price: item.suggested_retail_price
          }))
        };
        
        // 创建订单
        const newOrder = await procurementStore.addOrder(orderPayload);
        emit('created', newOrder);
      } catch (err) {
        console.error('创建订单失败:', err);
        error.value = err.message || '创建订单失败';
      } finally {
        submitting.value = false;
      }
    }
    
    return {
      orderData,
      submitting,
      error,
      addItem,
      removeItem,
      checkIsbnExists,
      calculateSubtotal,
      totalAmount,
      submitForm
    };
  }
};
</script>

<style scoped>
.order-form {
  max-width: 1000px;
}

.form-section {
  margin-bottom: 30px;
  border: 1px solid #eee;
  border-radius: 5px;
  padding: 20px;
  background-color: #fff;
}

.form-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #555;
}

.required {
  color: #e53935;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.isbn-input-group {
  display: flex;
  gap: 10px;
}

.isbn-input-group .form-control {
  flex: 1;
}

.isbn-input-group .btn {
  white-space: nowrap;
}

.book-exists-notice {
  color: #4caf50;
  margin-top: 5px;
  font-size: 12px;
}

.order-item {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
}

.order-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.order-item-header h4 {
  margin: 0;
}

.book-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.subtotal {
  text-align: right;
  margin-top: 15px;
  font-weight: bold;
  color: #333;
}

.order-total {
  font-size: 18px;
  font-weight: bold;
  text-align: right;
  margin-bottom: 20px;
  color: #2196f3;
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

.btn-primary {
  background-color: #2196f3;
  color: white;
}

.btn-secondary {
  background-color: #9e9e9e;
  color: white;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>