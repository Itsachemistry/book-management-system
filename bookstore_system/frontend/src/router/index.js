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
  {
    path: '/procurement',
    name: 'Procurement',
    component: () => import('../views/ProcurementView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/books',
    name: 'Books',
    component: () => import('../views/BookInventoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/sales',
    name: 'Sales',
    component: () => import('../views/SalesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/finance',
    name: 'Finance',
    component: () => import('../views/FinanceReportView.vue'),
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
  // 使用 import.meta.env.BASE_URL 确保基础路径与 Vite 配置一致
  // 在开发模式下，如果 vite.config.js 没有设置 base，BASE_URL 会是 '/'
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes
})

// 导航守卫
router.beforeEach(async (to, from, next) => {
  console.log(`路由导航: ${from.path} -> ${to.path}`);
  
  // 直接导入auth store，避免异步问题
  const { useAuthStore } = await import('../store/auth');
  const authStore = useAuthStore();
  
  // 检查身份验证状态
  const isAuthenticated = authStore.isAuthenticated;
  console.log(`认证状态: ${isAuthenticated}, 需要认证: ${!!to.meta.requiresAuth}`);
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('需要登录，重定向到登录页');
    next('/login');
  } 
  else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    console.log('需要管理员权限，重定向到首页');
    next('/');
  }
  else if (to.path === '/login' && isAuthenticated) {
    console.log('已登录，重定向到首页');
    next('/');
  }
  else {
    console.log('正常导航到:', to.path);
    next();
  }
})

export default router

