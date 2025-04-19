import { createRouter, createWebHistory } from 'vue-router'
// 导入你的视图组件 (现在是空的，先占位)
// import LoginView from '../views/LoginView.vue'
// import DashboardView from '../views/DashboardView.vue'

const routes = [
  // {
  //   path: '/login',
  //   name: 'Login',
  //   component: LoginView
  // },
  // {
  //   path: '/',
  //   name: 'Dashboard',
  //   component: DashboardView,
  //   meta: { requiresAuth: true } // 示例：标记需要登录才能访问
  // },
  // ... 其他路由将在后续阶段添加
  {
    path: '/:pathMatch(.*)*', // 捕获所有未匹配的路由
    name: 'NotFound',
    // 稍后创建 NotFoundView.vue
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // 使用 HTML5 History 模式
  routes
})

// 导航守卫 (将在阶段 1 添加)
// router.beforeEach((to, from, next) => {
//   // ... 检查登录状态逻辑
// })

export default router

