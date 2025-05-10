import api from './index';

/**
 * 获取所有用户列表
 * @returns {Promise<Array>} 用户列表
 */
export const getUsers = async () => {
  try {
    const response = await api.get('/users/');
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

/**
 * 获取单个用户信息
 * @param {Number} id 用户ID
 * @returns {Promise<Object>} 用户信息
 */
export const getUserById = async (id) => {
  try {
    const response = await api.get(`/users/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

/**
 * 创建新用户
 * @param {Object} userData 用户数据
 * @returns {Promise<Object>} 创建的用户数据
 */
export const createUser = async (userData) => {
  try {
    const response = await api.post('/users/', userData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

/**
 * 更新用户信息
 * @param {Number} id 用户ID
 * @param {Object} userData 更新的用户数据
 * @returns {Promise<Object>} 更新后的用户数据
 */
export const updateUserById = async (id, userData) => {
  try {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

/**
 * 删除用户
 * @param {Number} id 用户ID
 * @returns {Promise<Object>} 操作结果
 */
export const deleteUserById = async (id) => {
  try {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

/**
 * 更新当前用户资料
 * @param {Object} profileData 资料数据
 * @returns {Promise<Object>} 更新后的用户数据
 */
export const updateProfile = async (profileData) => {
  try {
    const response = await api.put('/users/me', profileData);
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

/**
 * 处理API错误
 * @param {Error} error 错误对象
 */
const handleApiError = (error) => {
  if (error.response) {
    // 服务器返回错误响应
    const status = error.response.status;
    const data = error.response.data;
    
    if (status === 400 && data.details) {
      // 验证错误，包含字段错误详情
      const err = new Error(data.error || '请求数据无效');
      err.details = data.details;
      throw err;
    } else if (status === 401) {
      // 未授权
      throw new Error('您没有权限执行此操作或会话已过期');
    } else if (status === 404) {
      // 资源未找到
      throw new Error('请求的资源不存在');
    } else {
      // 其他服务器错误
      throw new Error(data.error || '操作失败，请稍后再试');
    }
  } else if (error.request) {
    // 请求发送但没有收到响应
    throw new Error('无法连接到服务器，请检查您的网络连接');
  } else {
    // 请求设置过程中出错
    throw new Error('请求错误：' + error.message);
  }
};

