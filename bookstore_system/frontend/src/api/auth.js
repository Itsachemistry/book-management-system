import api from './index';

/**
 * 登录函数
 * @param {Object} credentials - 登录凭据
 * @param {string} credentials.username - 用户名
 * @param {string} credentials.password - 密码
 * @returns {Promise<Object>} 包含token和用户信息的响应
 */
export async function login(credentials) {
  try {
    console.log('发送登录请求:', credentials.username);
    const response = await api.post('/auth/login', credentials);
    console.log('登录成功，获取到token');
    return response.data;
  } catch (error) {
    console.error('登录失败:', error);
    if (error.response) {
      // 服务器返回的错误信息
      throw new Error(error.response.data.error || '登录失败，请检查用户名和密码');
    } else if (error.request) {
      // 请求已发出但未收到响应
      throw new Error('服务器无响应，请检查网络连接');
    } else {
      // 请求配置有误
      throw new Error('发送请求时出错');
    }
  }
}

/**
 * 获取当前登录用户信息
 * @returns {Promise<Object>} 用户信息
 */
export async function getCurrentUser() {
  try {
    console.log('获取当前用户信息');
    const response = await api.get('/auth/me');
    console.log('获取用户信息成功');
    return response.data;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    if (error.response && error.response.status === 401) {
      // 未授权，可能是token无效或过期
      throw new Error('会话已过期，请重新登录');
    } else if (error.response) {
      throw new Error(error.response.data.error || '获取用户信息失败');
    } else {
      throw new Error('无法连接到服务器');
    }
  }
}
