import { createApp } from 'vue'
import { createPinia } from 'pinia' 
import App from './App.vue'
import router from './router'

console.log('应用初始化开始...')

// 打印所有环境变量
console.log('env: ', import.meta.env);

// 创建Vue应用实例
const app = createApp(App)

// 创建Pinia实例
const pinia = createPinia()

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue错误:', err)
  console.error('错误信息:', info)
}

// 注册Pinia插件
app.use(pinia)

// 注册路由
app.use(router)

// 增加调试信息
console.log('环境:', import.meta.env.MODE)
console.log('API URL:', import.meta.env.VITE_API_BASE_URL)
console.log('准备挂载应用...')

// 挂载应用
app.mount('#app')
console.log('应用挂载完成!')

