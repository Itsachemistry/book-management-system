// filepath: c:\Users\Elio\Desktop\book-management-system\bookstore_system\frontend\src\App.vue
<template>
  <div id="app">
    <!-- 新增静态标题，用于验证页面是否渲染 -->
    <h1>书店管理系统 - 测试</h1>
    <router-view/>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useAuthStore } from './store/auth';

// 新增日志，用于验证组件脚本是否执行
console.log('App.vue loaded');

// 直接引用authStore，不使用ref
const authStore = useAuthStore();

// 登出方法
const logoutUser = () => {
  console.log('用户点击登出');
  authStore.logout();
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
