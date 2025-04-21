// filepath: c:\Users\Elio\Desktop\book-management-system\bookstore_system\frontend\src\App.vue
<template>
  <div class="app-container">
    <header class="app-header">
      <h1>书店管理系统</h1>
      <nav v-if="authStore.isAuthenticated">
        <router-link to="/">仪表板</router-link>
        <router-link to="/books">库存</router-link>
        <router-link to="/procurement">采购</router-link>
        <router-link to="/sales">销售</router-link>
        <router-link to="/reports">报表</router-link>
        <router-link v-if="authStore.isAdmin" to="/users">用户管理</router-link>
        <router-link to="/profile">个人资料</router-link>
        <button @click="logoutUser" class="logout-button">登出</button>
      </nav>
      <nav v-else>
        <router-link to="/login">登录</router-link>
      </nav>
    </header>
    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useAuthStore } from './store/auth';
import { useRouter } from 'vue-router';

// 新增日志，用于验证组件脚本是否执行
console.log('App.vue loaded');

// 直接引用authStore和router
const authStore = useAuthStore();
const router = useRouter();

// 登出方法
const logoutUser = () => {
  console.log('用户点击登出');
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  console.log('App组件已挂载, 初始化认证');
  // 初始化认证状态
  authStore.initialize();
  console.log('认证状态初始化完成, 用户已登录:', authStore.isAuthenticated);
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
