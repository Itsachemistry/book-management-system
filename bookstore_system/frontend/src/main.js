import { createApp } from 'vue'
import { createPinia } from 'pinia' // 导入 Pinia

import App from './App.vue'
import router from './router' // 导入路由配置 (下一步创建)

// 创建 Vue 应用实例
const app = createApp(App)

// 创建 Pinia 实例
const pinia = createPinia()

// 注册 Pinia 插件
app.use(pinia)
// 注册路由插件 (下一步创建)
app.use(router)

// 挂载应用
app.mount('#app') // 假设 public/index.html 中有一个 <div id="app"></div>

