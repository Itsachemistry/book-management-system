import axios from 'axios';

// 创建 Axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// 添加请求拦截器
apiClient.interceptors.request.use(config => {
  console.log(`请求: ${config.method.toUpperCase()} ${config.url}`, {
    params: config.params,
    data: config.data,
    headers: config.headers
  });

  // 从localStorage获取token
  const token = localStorage.getItem('auth_token');
  
  // 如果有token，添加到请求头
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // POST和PUT请求时确保数据正确
  if ((config.method === 'post' || config.method === 'put') && config.data) {
    // 确保数值类型字段正确转换
    if (typeof config.data === 'object' && !(config.data instanceof FormData)) {
      // 特别处理Books API相关字段
      if (config.data.retail_price !== undefined) {
        config.data.retail_price = Number(config.data.retail_price);
      }
      if (config.data.quantity !== undefined) {
        config.data.quantity = Number(config.data.quantity);
      }
      
      // 处理布尔类型
      if (config.data.is_active !== undefined) {
        // 确保是布尔值类型，而不是数字类型
        config.data.is_active = Boolean(config.data.is_active);
      }
      
      // 特别处理创建书籍的API调用 - 移除is_active字段
      if (config.url === '/books' && config.method === 'post') {
        const { is_active, ...dataWithoutIsActive } = config.data;
        config.data = dataWithoutIsActive;
      }
    }
  }
  
  return config;
}, error => {
  console.error('请求拦截器错误:', error);
  return Promise.reject(error);
});

// 添加响应拦截器
apiClient.interceptors.response.use(response => {
  console.log(`响应: ${response.status} ${response.config.method.toUpperCase()} ${response.config.url}`, {
    data: response.data
  });
  return response;
}, error => {
  console.error('响应拦截器捕获错误:', error);

  // 日志完整错误信息以便调试
  if (error.response) {
    console.error('API错误响应:', {
      状态码: error.response.status,
      响应数据: error.response.data,
      请求: error.config
    });
    
    // 401错误时可能需要重新登录
    if (error.response.status === 401) {
      // 如果不是登录请求本身，可以清除token并重定向到登录页面
      if (!error.config.url.includes('login')) {
        console.log('认证失败，清除token');
        localStorage.removeItem('auth_token');
        // 如果使用了Vue Router，这里可以重定向
        // window.location.href = '/login';
      }
    }
  } else {
    console.error('API请求错误:', error.message);
  }
  
  return Promise.reject(error);
});

export default apiClient;

