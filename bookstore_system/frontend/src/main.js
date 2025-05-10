import { createApp } from 'vue'
import { createPinia } from 'pinia' 
import App from './App.vue'
import router from './router'
import { useAuthStore } from './store/auth'; // 导入 auth store

console.log('应用初始化开始...')

// 打印所有环境变量
console.log('env: ', import.meta.env);

// 创建Vue应用实例
const app = createApp(App)

// 创建Pinia实例
const pinia = createPinia()

// 注册Pinia插件
app.use(pinia)

// 在注册路由和挂载应用前初始化Auth Store
const authStore = useAuthStore(); // 获取 auth store 实例

async function initializeAppAndMount() {
  try {
    console.log('开始初始化 Auth Store...');
    await authStore.initialize();
    console.log('Auth Store 初始化完成。 isAuthenticated:', authStore.isAuthenticated);
  } catch (error) {
    console.error('Auth Store 初始化失败:', error);
    // 根据需要处理关键的初始化失败
  }

  // 注册路由 (在 auth store 初始化后)
  app.use(router)
  console.log('路由已注册。');

  // 增加调试信息
  console.log('环境:', import.meta.env.MODE)
  console.log('API URL:', import.meta.env.VITE_API_BASE_URL)
  console.log('准备挂载应用...')

  // 挂载应用
  app.mount('#app')
  console.log('应用挂载完成!')
}

// 调用异步初始化函数
initializeAppAndMount();

