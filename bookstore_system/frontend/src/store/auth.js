import { defineStore } from 'pinia';
import { login as loginApi, getCurrentUser as fetchCurrentUser } from '../api/auth';
import router from '../router';
import apiClient from '../api'; // <--- 静态导入 apiClient

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
    status: 'idle', // 'idle' | 'loading' | 'success' | 'error'
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'SUPER_ADMIN' || state.user?.role === 'NORMAL_ADMIN',
    isSuperAdmin: (state) => state.user?.role === 'SUPER_ADMIN',
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
        localStorage.setItem('auth_token', response.token);  // 修改为'auth_token'
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
      localStorage.removeItem('auth_token');  // 修改为'auth_token'
      localStorage.removeItem('user');
      
      // 清除 axios 授权头
      this.clearAuthHeader();
      
      // 重定向到登录页
      router.push('/login');
    },
    
    async getCurrentUser() {
      this.status = 'loading';
      this.error = null; // 重置错误状态
      
      try {
        const user = await fetchCurrentUser();
        this.user = user;
        this.status = 'success';
        // 成功获取用户后，也更新localStorage中的用户信息
        localStorage.setItem('user', JSON.stringify(user));
        return user;
      } catch (error) {
        this.status = 'error';
        this.error = error.message;
        // 如果获取当前用户失败（通常意味着token无效或过期）
        // 后端应为无效token返回401
        if ((error.response && error.response.status === 401) || error.message.includes('会话已过期')) {
          console.log('getCurrentUser 失败或会话过期，执行登出:', error.message);
          this.logout(); // 调用logout清理状态并重定向
        }
        throw error; // 重新抛出错误，以便调用者可以处理
      }
    },
    
    async initialize() {
      console.log('初始化认证状态...');
      const token = localStorage.getItem('auth_token');
      console.log('从localStorage读取到token:', token ? '存在' : '不存在');
      
      if (token) {
        this.token = token; // 先设置token，以便API请求可以使用它
        this.setAuthHeader(); // 立即设置axios的默认头

        try {
          // 尝试获取当前用户信息以验证token是否仍然有效
          await this.getCurrentUser();
          console.log('认证状态初始化成功，用户:', this.user ? this.user.username : '未知');
        } catch (error) {
          // 如果 getCurrentUser 失败 (内部已调用 logout)，这里不需要额外操作
          console.log('initialize 时，令牌验证失败或获取用户信息失败:', error.message);
          // getCurrentUser 内部的 logout 会处理清理和重定向
          // 如果 getCurrentUser 由于某种原因未触发 logout (例如，不是401错误)，
          // 但我们仍然认为 token 无效，则可能需要手动 logout。
          // 但通常 getCurrentUser 的 401 处理就足够了。
        }
      } else {
        // 如果本地没有token，确保是登出状态，但不立即重定向
        console.log('No token found in localStorage. Clearing auth state without redirect.');
        this.token = null;
        this.user = null;
        this.status = 'idle'; // 重置状态
        this.error = null;    // 重置错误
        this.clearAuthHeader(); // 清除 axios 默认授权头
      }
    },
    
    // 辅助方法：设置 axios 默认授权头
    setAuthHeader() {
      if (this.token) {
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        console.log('已设置默认授权头');
      }
    },
    
    // 辅助方法：清除 axios 授权头
    clearAuthHeader() {
      delete apiClient.defaults.headers.common['Authorization'];
      console.log('已清除默认授权头');
    }
  }
});

