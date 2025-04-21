<template>
  <div class="login-container">
    <div class="login-form">
      <h1>书店管理系统</h1>
      <h2>登录</h2>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            id="username" 
            v-model="username" 
            type="text" 
            required 
            autocomplete="username"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password" 
            v-model="password" 
            type="password" 
            required 
            autocomplete="current-password"
          />
        </div>
        
        <div class="form-actions">
          <button type="submit" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('admin');
const password = ref('admin123');
const loading = ref(false);
const error = ref('');

const login = async () => {
  error.value = '';
  loading.value = true;
  
  try {
    await authStore.login({
      username: username.value,
      password: password.value
    });
    router.push('/');
  } catch (err) {
    error.value = err.message || '登录失败，请检查用户名和密码';
    console.error('登录失败:', err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-form {
  width: 90%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

h1 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  text-align: center;
  font-size: 1.8rem;
}

h2 {
  margin-bottom: 2rem;
  color: #2c3e50;
  text-align: center;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #2c3e50;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.error-message {
  padding: 0.75rem;
  margin-bottom: 1.5rem;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 4px;
}
</style>

