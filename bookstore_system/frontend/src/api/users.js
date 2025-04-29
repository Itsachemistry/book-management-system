import api from './index';

/**
 * 创建新用户（需要管理员权限）
 * @param {Object} userData 用户数据
 * @returns {Promise<Object>} 创建的用户信息
 */
export async function createUser(userData) {
  try {
    const response = await api.post('/users/', userData);
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      // 提取详细的验证错误信息
      const errorResponse = error.response.data;
      const errorMessage = errorResponse.error || '创建用户失败';
      
      // 创建一个包含错误消息和详细信息的自定义错误对象
      const customError = new Error(errorMessage);
      if (errorResponse.details) {
        customError.details = errorResponse.details;
      }
      throw customError;
    }
    
    // 兜底的错误处理
    throw new Error('创建用户失败');
  }
}

/**
 * 获取所有用户列表（需要管理员权限）
 * @returns {Promise<Array>} 用户列表
 */
export async function getUsers() {
  try {
    const response = await api.get('/users/');
    return response.data;
  } catch (error) {
    handleApiError(error, '获取用户列表失败');
  }
}

/**
 * 更新当前用户的个人资料
 * @param {Object} profileData 要更新的资料数据
 * @returns {Promise<Object>} 更新后的用户信息
 */
export async function updateProfile(profileData) {
  try {
    const response = await api.put('/users/me', profileData);
    return response.data;
  } catch (error) {
    handleApiError(error, '更新个人资料失败');
  }
}

/**
 * 统一的API错误处理
 * @param {Error} error Axios错误对象
 * @param {string} defaultMessage 默认错误信息
 */
function handleApiError(error, defaultMessage) {
  if (error.response) {
    // 服务器返回了错误状态码
    const message = error.response.data.error || defaultMessage;
    
    if (error.response.status === 401) {
      throw new Error('会话已过期，请重新登录');
    } else if (error.response.status === 403) {
      throw new Error('您没有执行此操作的权限');
    }
    
    throw new Error(message);
  } else if (error.request) {
    // 请求已发出但未收到响应
    throw new Error('无法连接到服务器，请检查网络连接');
  } else {
    // 请求配置有误
    throw new Error('发送请求时出错');
  }
}

