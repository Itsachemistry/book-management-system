<template>
  <div class="not-found-container">
    <h1>404</h1>
    <h2>页面不存在</h2>
    <p>您访问的页面不存在或已被移除</p>
    <router-link to="/" class="back-button">返回首页</router-link>
  </div>
</template>

<script setup>
// 不需要特殊逻辑
</script>

<style scoped>
.not-found-container {
  text-align: center;
  padding: 3rem;
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  font-size: 6rem;
  margin: 0;
  color: #e74c3c;
}

h2 {
  margin: 0;
  font-size: 2rem;
  color: #34495e;
  margin-bottom: 1rem;
}

p {
  color: #7f8c8d;
  margin-bottom: 2rem;
}

.back-button {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.back-button:hover {
  background-color: #2980b9;
}
</style>

