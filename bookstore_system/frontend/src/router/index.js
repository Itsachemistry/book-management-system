import { createRouter, createWebHistory } from 'vue-router'

// 路由定义
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('../views/UserManagementView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  // 其他路由将在后续阶段添加
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // 使用 HTML5 History 模式
  routes
})

// 导航守卫
router.beforeEach(async (to, from, next) => {
  // 动态导入auth store以避免循环依赖
  const { useAuthStore } = await import('../store/auth');
  const authStore = useAuthStore();
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 需要登录但未认证，重定向到登录页
    next('/login');
  } 
  else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    // 需要管理员权限但不是管理员，重定向到首页
    next('/');
  }
  else if (to.path === '/login' && authStore.isAuthenticated) {
    // 已登录用户尝试访问登录页，重定向到首页
    next('/');
  }
  else {
    // 正常导航
    next();
  }
})

export default router

