// filepath: c:\Users\Elio\Desktop\book-management-system\bookstore_system\frontend\src\App.vue
<template>
  <div class="app-container">
    <header v-if="authStore.isAuthenticated" class="app-header">
      <h1>书店管理系统</h1>
      <nav>
        <router-link to="/">主页</router-link>
        <router-link v-if="authStore.isAdmin" to="/users">用户管理</router-link>
        <router-link to="/profile">个人资料</router-link>
        <button @click="authStore.logout" class="logout-button">退出登录</button>
      </nav>
    </header>
    
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from './store/auth';

const authStore = useAuthStore();

onMounted(() => {
  // 应用启动时初始化认证状态
  authStore.initialize();
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #333;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2c3e50;
  color: white;
}

.app-header h1 {
  font-size: 1.5rem;
}

.app-header nav {
  display: flex;
  gap: 1.5rem;
}

.app-header a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 0;
}

.app-header a.router-link-active {
  font-weight: bold;
  border-bottom: 2px solid white;
}

.app-content {
  flex: 1;
}

.logout-button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.5rem 0;
}

.logout-button:hover {
  text-decoration: underline;
}
</style>
