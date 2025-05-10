<template>
  <div class="book-inventory">
    <h1>图书库存管理</h1>

    <div class="top-actions">
      <div class="action-buttons">
        <!-- 现有的添加按钮 -->
        <button 
          v-if="authStore.isAdmin" 
          class="btn btn-primary" 
          @click="showAddModal = true"
        >
          添加书籍
        </button>
        
        <!-- 新增批量导入按钮 -->
        <router-link to="/books/import" class="btn btn-secondary">
          <i class="fas fa-file-import"></i> 批量导入
        </router-link>
        
        <!-- 新增的ISBN查询按钮 -->
        <router-link to="/books/isbn-references" class="btn btn-info">
          <i class="fas fa-search"></i> ISBN引用查询
        </router-link>
      </div>
    </div>

    <!-- 搜索和过滤 -->
    <BookSearchFilter
      :initial-search="bookStore.searchParams.search"
      :initial-per-page="bookStore.searchParams.per_page"
      :initial-active-only="bookStore.searchParams.active_only"
      @search="handleSearch"
      @filter-change="handleFilterChange"
      @per-page-change="handlePerPageChange"
    />

    <!-- 错误提示 -->
    <div v-if="bookStore.error" class="error-message">
      {{ bookStore.error }}
      <button class="close-btn" @click="bookStore.clearError">&times;</button>
    </div>

    <!-- 书籍表格 -->
    <BookTable
      :books="bookStore.books || []"
      :pagination="bookStore.pagination || { page: 1, per_page: 20, total: 0, pages: 0 }"
      :loading="bookStore.loading"
      :is-admin="authStore.isAdmin"
      @edit="handleEdit"
      @delete="handleDelete"
      @view="handleView"
      @change-page="handlePageChange"
    />

    <!-- 添加书籍模态框 -->
    <div v-if="showAddModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>添加新书籍</h2>
          <button class="close-btn" @click="showAddModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <BookForm
            :loading="bookStore.loading"
            @save="handleAddBook"
            @cancel="showAddModal = false"
          />
        </div>
      </div>
    </div>

    <!-- 编辑书籍模态框 -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>编辑书籍</h2>
          <button class="close-btn" @click="showEditModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <BookForm
            :book="selectedBook"
            :is-edit-mode="true"
            :loading="bookStore.loading"
            @save="handleUpdateBook"
            @cancel="showEditModal = false"
          />
        </div>
      </div>
    </div>

    <!-- 查看书籍详情模态框 -->
    <div v-if="showViewModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>书籍详情</h2>
          <button class="close-btn" @click="showViewModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <BookDetail 
            :book="selectedBook" 
            :isAdmin="authStore.isAdmin"
            @close="showViewModal = false"
            @edit="handleEditFromView"
          />
        </div>
      </div>
    </div>

    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content delete-modal">
        <div class="modal-header">
          <h2>确认删除</h2>
          <button class="close-btn" @click="showDeleteModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <p>您确定要删除以下书籍吗？</p>
          <p class="delete-book-name">《{{ selectedBook.name }}》</p>
          <p class="delete-warning">此操作将从数据库中永久删除该书籍，无法恢复！如果该书籍已有销售或采购记录，删除可能会失败。</p>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showDeleteModal = false">取消</button>
            <button 
              class="btn-delete" 
              @click="confirmDelete"
              :disabled="bookStore.loading"
            >
              {{ bookStore.loading ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useBookStore } from '../store/book';
import { useAuthStore } from '../store/auth';
import BookTable from '../components/BookTable.vue';
import BookForm from '../components/BookForm.vue';
import BookSearchFilter from '../components/BookSearchFilter.vue';
import BookDetail from '../components/BookDetail.vue'; // 导入新组件

// 获取 store 实例
const bookStore = useBookStore();
const authStore = useAuthStore();

// 模态框状态
const showAddModal = ref(false);
const showEditModal = ref(false);
const showViewModal = ref(false);
const showDeleteModal = ref(false);

// 选中的书籍
const selectedBook = ref({});

// 组件挂载时加载书籍列表
onMounted(async () => {
  try {
    console.log('[BookInventoryView - onMounted] 组件挂载，开始加载书籍数据');
    await bookStore.loadBooks();
    // 1. 打印组件层面获取到的数据
    console.log('[BookInventoryView - onMounted] 书籍数据加载完成, bookStore.books:', JSON.stringify(bookStore.books, null, 2));
    console.log('[BookInventoryView - onMounted] 分页数据加载完成, bookStore.pagination:', JSON.stringify(bookStore.pagination, null, 2));
  } catch (error) {
    console.error('[BookInventoryView - onMounted] 加载书籍列表失败:', error);
  }
});

// 搜索处理
function handleSearch(query) {
  bookStore.loadBooks({ search: query, page: 1 });
}

// 过滤条件变化处理
function handleFilterChange(filters) {
  bookStore.loadBooks({ ...filters, page: 1 });
}

// 每页数量变化处理
function handlePerPageChange(perPage) {
  bookStore.loadBooks({ per_page: perPage, page: 1 });
}

// 分页处理
function handlePageChange(page) {
  bookStore.loadBooks({ page });
}

// 处理添加书籍
async function handleAddBook(bookData) {
  try {
    console.log('准备添加新书籍:', bookData);
    await bookStore.addBook(bookData);
    showAddModal.value = false;
    // 刷新列表
    await bookStore.loadBooks();
  } catch (error) {
    console.error('添加书籍失败:', error);
    alert('添加书籍失败: ' + (error.message || '未知错误'));
  }
}

// 处理编辑请求
function handleEdit(book) {
  selectedBook.value = { ...book };
  showEditModal.value = true;
}

// 从详情视图切换到编辑
function handleEditFromView() {
  showViewModal.value = false;
  showEditModal.value = true;
}

// 处理更新书籍
async function handleUpdateBook(bookData) {
  try {
    await bookStore.editBook(selectedBook.value.id, bookData);
    showEditModal.value = false;
    // 刷新列表，确保显示最新数据
    await bookStore.loadBooks();
  } catch (error) {
    console.error('更新书籍失败:', error);
  }
}

// 处理查看详情
function handleView(book) {
  selectedBook.value = { ...book };
  showViewModal.value = true;
  console.log('显示书籍详情:', selectedBook.value); // 添加日志以便调试
}

// 处理删除请求
function handleDelete(book) {
  selectedBook.value = { ...book };
  showDeleteModal.value = true;
}

// 确认删除
async function confirmDelete() {
  try {
    await bookStore.removeBook(selectedBook.value.id);
    showDeleteModal.value = false;
    // 刷新列表，确保显示最新数据
    await bookStore.loadBooks();
  } catch (error) {
    console.error('删除书籍失败:', error);
  }
}

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
.book-inventory {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.top-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.btn-primary {
  background-color: #3498db;
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-info {
  background-color: #3498db;
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-info:hover {
  background-color: #2980b9;
}

.error-message {
  color: #e74c3c;
  background-color: #f2dede;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-body {
  margin-bottom: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-cancel {
  background-color: #95a5a6;
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
  margin-right: 10px;
}

.btn-cancel:hover {
  background-color: #7f8c8d;
}

.btn-edit {
  background-color: #f39c12;
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
}

.btn-edit:hover {
  background-color: #e67e22;
}

.btn-delete {
  background-color: #e74c3c;
  color: #fff;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
}

.btn-delete:hover {
  background-color: #c0392b;
}

.delete-modal {
  width: 400px;
}

.delete-book-name {
  font-weight: bold;
  margin: 10px 0;
}

.delete-warning {
  color: #e74c3c;
  font-size: 14px;
}

.book-details {
  padding: 10px;
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
</style>

