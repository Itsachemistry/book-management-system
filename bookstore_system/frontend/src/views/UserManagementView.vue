<template>
  <div class="user-management">
    <h1>用户管理</h1>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div class="actions">
      <button @click="showCreateModal = true" class="btn-primary">
        创建新用户
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <table v-else class="users-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>全名</th>
          <th>员工ID</th>
          <th>性别</th>
          <th>年龄</th>
          <th>角色</th>
          <th>创建时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.full_name || '-' }}</td>
          <td>{{ user.employee_id }}</td>
          <td>{{ user.gender || '-' }}</td>
          <td>{{ user.age || '-' }}</td>
          <td>{{ user.role }}</td>
          <td>{{ formatDate(user.created_at) }}</td>
        </tr>
      </tbody>
    </table>
    
    <!-- 创建用户模态框 -->
    <div v-if="showCreateModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>创建新用户</h2>
          <button @click="showCreateModal = false" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <div v-if="formError" class="error-message">
            {{ formError }}
          </div>
          
          <form @submit.prevent="createNewUser">
            <div class="form-group">
              <label for="username">用户名<span class="required">*</span></label>
              <input type="text" id="username" v-model="newUser.username" required>
            </div>
            
            <div class="form-group">
              <label for="password">密码<span class="required">*</span></label>
              <input type="password" id="password" v-model="newUser.password" required>
              <span v-if="newUser.password && newUser.password.length < 6" class="error-hint">
                密码长度必须至少为6个字符
              </span>
            </div>
            
            <div class="form-group">
              <label for="employee_id">员工ID<span class="required">*</span></label>
              <input type="text" id="employee_id" v-model="newUser.employee_id" required>
            </div>
            
            <div class="form-group">
              <label for="full_name">全名</label>
              <input type="text" id="full_name" v-model="newUser.full_name">
            </div>
            
            <div class="form-group">
              <label for="gender">性别</label>
              <select id="gender" v-model="newUser.gender">
                <option value="">请选择</option>
                <option value="男">男</option>
                <option value="女">女</option>
                <option value="其他">其他</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="age">年龄</label>
              <input type="number" id="age" v-model.number="newUser.age" min="18">
            </div>
            
            <div class="form-group">
              <label for="role">角色<span class="required">*</span></label>
              <select id="role" v-model="newUser.role" required>
                <option value="NORMAL_ADMIN">普通管理员</option>
                <option value="SUPER_ADMIN">超级管理员</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="showCreateModal = false" class="btn-secondary">
                取消
              </button>
              <button type="submit" class="btn-primary" :disabled="formSubmitting">
                {{ formSubmitting ? '创建中...' : '创建用户' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getUsers, createUser } from '../api/users';
import { useAuthStore } from '../store/auth';

// 检查是否是管理员
const authStore = useAuthStore();
if (!authStore.isAdmin) {
  // 如果不是管理员，可以跳转回首页或显示错误
}

// 状态变量
const users = ref([]);
const loading = ref(true);
const error = ref(null);
const showCreateModal = ref(false);
const formError = ref(null);
const formSubmitting = ref(false);

// 新用户表单数据
const newUser = ref({
  username: '',
  password: '',
  employee_id: '',
  full_name: '',
  gender: '',
  age: null,
  role: 'NORMAL_ADMIN'
});

// 格式化日期显示
function formatDate(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString();
}

// 获取用户列表
async function fetchUsers() {
  loading.value = true;
  error.value = null;
  
  try {
    users.value = await getUsers();
  } catch (err) {
    error.value = err.message;
    console.error('获取用户列表失败:', err);
  } finally {
    loading.value = false;
  }
}

// 创建新用户
async function createNewUser() {
  formSubmitting.value = true;
  formError.value = null;
  
  // 添加表单验证
  if (newUser.value.password && newUser.value.password.length < 6) {
    formError.value = "密码长度必须至少为6个字符";
    formSubmitting.value = false;
    return;
  }
  
  try {
    await createUser(newUser.value);
    showCreateModal.value = false;
    
    // 重置表单
    newUser.value = {
      username: '',
      password: '',
      employee_id: '',
      full_name: '',
      gender: '',
      age: null,
      role: 'NORMAL_ADMIN'
    };
    
    // 刷新用户列表
    fetchUsers();
  } catch (err) {
    // 处理详细的验证错误
    if (err.details) {
      if (err.details.employee_id) {
        formError.value = `员工ID错误: ${err.details.employee_id.join(', ')}`;
      } else if (err.details.username) {
        formError.value = `用户名错误: ${err.details.username.join(', ')}`;
      } else {
        formError.value = err.message || "创建用户失败";
      }
    } else {
      formError.value = err.message || "创建用户失败";
    }
  } finally {
    formSubmitting.value = false;
  }
}

// 组件挂载时获取用户列表
onMounted(fetchUsers);
</script>

<style scoped>
.user-management {
  padding: 2rem;
}

h1 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

.actions {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #7f8c8d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.users-table th,
.users-table td {
  border: 1px solid #ddd;
  padding: 0.75rem;
  text-align: left;
}

.users-table th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.users-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border-radius: 4px;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-body {
  padding: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #34495e;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.required {
  color: #e74c3c;
  margin-left: 0.25rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.error-hint {
  color: #e74c3c;
  font-size: 0.8rem;
  display: block;
  margin-top: 0.25rem;
}
</style>

