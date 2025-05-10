import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'; // Import auth store

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
    meta: { requiresAuth: true, requiresSuperAdmin: true } // 只有超级管理员可以管理用户
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
    meta: { requiresAuth: true, requiresAdmin: true } // 普通管理员和超级管理员都可以
  },
  {
    path: '/books',
    name: 'Books',
    component: () => import('../views/BookInventoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/books/import',
    name: 'BookImport',
    component: () => import('../views/BulkImportView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/books/isbn-references',
    name: 'IsbnReferences',
    component: () => import('../views/IsbnReferenceView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/sales',
    name: 'Sales',
    component: () => import('../views/SalesView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/finance',
    name: 'Finance',
    component: () => import('../views/FinanceReportView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
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
router.beforeEach((to, from, next) => {
  console.log(`路由导航: ${from.path} -> ${to.path}`);
  
  // authStore 应该在 main.js 中 initializeAppAndMount 调用时已实例化并初始化
  const auth = useAuthStore(); 
  
  // 确保 auth.initialize() 已完成（通过 main.js 中的 await）
  // isAuthenticated getter 现在是主要的检查点
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    console.log(`需要认证的路由 (${to.path}) 但用户未认证 (isAuthenticated: ${auth.isAuthenticated})，重定向到登录`);
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.meta.requiresSuperAdmin && !auth.isSuperAdmin) {
    console.log(`需要超级管理员权限的路由 (${to.path}) 但用户不是超级管理员，重定向到 Dashboard`);
    next({ name: 'Dashboard' });
  } else if (to.meta.requiresAdmin && !auth.isAdmin) {
    console.log(`需要管理员权限的路由 (${to.path}) 但用户不是管理员或未认证，重定向到 Dashboard`);
    next({ name: 'Dashboard' }); 
  } else {
    console.log(`正常导航到: ${to.path} (isAuthenticated: ${auth.isAuthenticated})`);
    next();
  }
});

export default router

