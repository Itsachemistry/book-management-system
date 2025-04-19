import { defineStore } from 'pinia';
import { login as loginApi, getCurrentUser } from '../api/auth';
import router from '../router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
    status: 'idle', // 'idle' | 'loading' | 'success' | 'error'
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'SUPER_ADMIN',
    isLoading: (state) => state.status === 'loading'
  },
  
  actions: {
    async login(credentials) {
      this.status = 'loading';
      this.error = null;
      
      try {
        const response = await loginApi(credentials);
        
        // 保存到 state
        this.token = response.token;
        this.user = response.user;
        this.status = 'success';
        
        // 保存到 localStorage（持久化）
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        // 设置 axios 默认授权头
        this.setAuthHeader();
        
        return response.user;
      } catch (error) {
        this.status = 'error';
        this.error = error.message;
        throw error;
      }
    },
    
    logout() {
      // 清除 state
      this.token = null;
      this.user = null;
      this.status = 'idle';
      this.error = null;
      
      // 清除 localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // 清除 axios 授权头
      this.clearAuthHeader();
      
      // 重定向到登录页
      router.push('/login');
    },
    
    async getCurrentUser() {
      this.status = 'loading';
      
      try {
        const user = await getCurrentUser();
        this.user = user;
        this.status = 'success';
        return user;
      } catch (error) {
        if (error.message.includes('会话已过期')) {
          // 如果token无效，执行登出操作
          this.logout();
        }
        this.status = 'error';
        this.error = error.message;
        throw error;
      }
    },
    
    initialize() {
      // 应用加载时从 localStorage 恢复会话
      const token = localStorage.getItem('token');
      const user = localStorage.getItem('user');
      
      if (token && user) {
        try {
          this.token = token;
          this.user = JSON.parse(user);
          this.setAuthHeader();
          
          // 验证令牌是否仍然有效
          this.getCurrentUser().catch(() => {
            // 令牌无效时会自动登出
          });
        } catch (error) {
          // JSON 解析错误或其他问题
          this.logout();
        }
      }
    },
    
    // 辅助方法：设置 axios 默认授权头
    setAuthHeader() {
      if (this.token) {
        import('../api').then(module => {
          const api = module.default;
          api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        });
      }
    },
    
    // 辅助方法：清除 axios 授权头
    clearAuthHeader() {
      import('../api').then(module => {
        const api = module.default;
        delete api.defaults.headers.common['Authorization'];
      });
    }
  }
});

