<template>
  <div class="dashboard-container">
    <h1>仪表板</h1>
    <div class="welcome-message">
      <p>欢迎回来，{{ authStore.user?.full_name || authStore.user?.username }}</p>
      <p>你的角色：{{ authStore.user?.role === 'SUPER_ADMIN' ? '超级管理员' : '普通管理员' }}</p>
    </div>
    
    <div class="dashboard-cards">
      <div class="card">
        <h3>用户管理</h3>
        <p v-if="authStore.isAdmin">
          您可以管理系统用户。
          <router-link to="/users">查看用户列表</router-link>
        </p>
        <p v-else>
          您可以在个人资料页面更新您的信息。
          <router-link to="/profile">前往个人资料</router-link>
        </p>
      </div>
      
      <!-- 这些功能将在后续阶段实现 -->
      <div class="card">
        <h3>图书库存</h3>
        <p>管理书籍库存、查询图书信息。</p>
        <p><router-link to="/books">管理图书</router-link></p>
      </div>
      
      <div class="card">
        <h3>图书采购</h3>
        <p>创建采购单、追踪采购状态、管理入库。</p>
        <p><router-link to="/procurement">前往采购管理</router-link></p>
      </div>
      
      <div class="card">
        <h3>销售管理</h3>
        <p>处理书籍销售、查看销售记录。</p>
        <p><router-link to="/sales">前往销售页面</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
}

h1 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.welcome-message {
  background-color: #ebf5fb;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.welcome-message p {
  margin: 0.5rem 0;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card h3 {
  color: #3498db;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.card p {
  margin: 0.5rem 0;
}

a {
  color: #3498db;
  text-decoration: none;
  font-weight: bold;
}

a:hover {
  text-decoration: underline;
}
</style>

