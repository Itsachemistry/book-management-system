<template>
  <div class="profile-container">
    <h1>个人资料</h1>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="success" class="success-message">
      {{ success }}
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else class="profile-content">
      <div class="profile-info">
        <h2>账户信息</h2>
        <div class="info-row">
          <div class="info-label">用户名</div>
          <div class="info-value">{{ userData.username }}</div>
        </div>
        <div class="info-row">
          <div class="info-label">员工ID</div>
          <div class="info-value">{{ userData.employee_id }}</div>
        </div>
        <div class="info-row">
          <div class="info-label">角色</div>
          <div class="info-value">
            {{ userData.role === 'SUPER_ADMIN' ? '超级管理员' : '普通管理员' }}
          </div>
        </div>
      </div>
      
      <div class="profile-edit">
        <h2>编辑个人资料</h2>
        <form @submit.prevent="updateUserProfile">
          <div class="form-group">
            <label for="full_name">全名</label>
            <input type="text" id="full_name" v-model="form.full_name">
          </div>
          
          <div class="form-group">
            <label for="gender">性别</label>
            <select id="gender" v-model="form.gender">
              <option value="">请选择</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="其他">其他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="age">年龄</label>
            <input type="number" id="age" v-model.number="form.age" min="18">
          </div>
          
          <button 
            type="submit" 
            class="update-button"
            :disabled="updating"
          >
            {{ updating ? '更新中...' : '更新资料' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../store/auth';
import { updateProfile } from '../api/users';

const authStore = useAuthStore();
const userData = computed(() => authStore.user || {});

// 状态变量
const loading = ref(false);
const updating = ref(false);
const error = ref(null);
const success = ref(null);

// 表单数据
const form = ref({
  full_name: '',
  gender: '',
  age: null
});

// 初始化表单数据
function initFormData() {
  if (userData.value) {
    form.value.full_name = userData.value.full_name || '';
    form.value.gender = userData.value.gender || '';
    form.value.age = userData.value.age || null;
  }
}

// 更新用户资料
async function updateUserProfile() {
  if (!authStore.isAuthenticated) {
    error.value = '请先登录';
    return;
  }
  
  updating.value = true;
  error.value = null;
  success.value = null;
  
  try {
    // 过滤掉空值，只发送有值的字段
    const profileData = {};
    
    if (form.value.full_name) {
      profileData.full_name = form.value.full_name;
    }
    
    if (form.value.gender) {
      profileData.gender = form.value.gender;
    }
    
    if (form.value.age !== null && form.value.age !== '') {
      profileData.age = form.value.age;
    }
    
    const updatedUser = await updateProfile(profileData);
    
    // 更新store中的用户数据
    authStore.user = updatedUser;
    
    // 更新localStorage中的用户数据
    localStorage.setItem('user', JSON.stringify(updatedUser));
    
    success.value = '个人资料更新成功';
  } catch (err) {
    error.value = err.message;
    console.error('更新资料失败:', err);
  } finally {
    updating.value = false;
  }
}

// 组件挂载时初始化表单数据
onMounted(() => {
  loading.value = true;
  
  if (!authStore.user) {
    // 如果store中没有用户数据，尝试获取
    authStore.getCurrentUser()
      .then(() => {
        initFormData();
      })
      .catch(err => {
        error.value = err.message;
      })
      .finally(() => {
        loading.value = false;
      });
  } else {
    initFormData();
    loading.value = false;
  }
});
</script>

<style scoped>
.profile-container {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 2rem;
  color: #2c3e50;
}

h2 {
  color: #34495e;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.profile-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
}

.profile-info, .profile-edit {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.info-row {
  display: flex;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-label {
  width: 120px;
  color: #7f8c8d;
}

.info-value {
  flex: 1;
  font-weight: 500;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #34495e;
}

input, select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.update-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.update-button:hover {
  background-color: #2980b9;
}

.update-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
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

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border-radius: 4px;
}
</style>