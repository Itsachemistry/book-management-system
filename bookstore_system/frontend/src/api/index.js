import axios from 'axios';

// 创建 Axios 实例
const apiClient = axios.create({
  // 从 Vite 环境变量读取后端 API 的基础 URL
  // 需要在 frontend/.env.development 文件中定义 VITE_API_BASE_URL
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api', // 提供一个默认值
  headers: {
    'Content-Type': 'application/json',
  }
});

// (可选) 添加请求拦截器 - 例如，在每个请求中附加认证 Token
// apiClient.interceptors.request.use(config => {
//   const token = localStorage.getItem('authToken'); // 假设 token 存储在 localStorage
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// }, error => {
//   return Promise.reject(error);
// });

// (可选) 添加响应拦截器 - 例如，处理全局错误或 Token 过期
// apiClient.interceptors.response.use(response => {
//   return response;
// }, error => {
//   if (error.response && error.response.status === 401) {
//     // 处理未授权错误，例如重定向到登录页
//     console.error("Unauthorized access - redirecting to login");
//     // store.dispatch('auth/logout'); // 假设有 logout action
//     // router.push('/login');
//   }
//   return Promise.reject(error);
// });

export default apiClient;

