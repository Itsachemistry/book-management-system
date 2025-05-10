import api from './index';

export const getSales = async (params = {}) => {
  try {
    console.log('获取销售列表请求参数:', params);
    const response = await api.get('/sales', { 
      params,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    console.log('获取销售列表成功:', response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, '获取销售列表失败');
  }
};

export const getSale = async (id) => {
  try {
    console.log(`获取销售详情 ID:${id}`);
    const response = await api.get(`/sales/${id}`);
    console.log('获取销售详情成功:', response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, '获取销售详情失败');
  }
};

export const createSale = async (saleData) => {
  try {
    // 检查Token是否存在
    const token = localStorage.getItem('auth_token');
    console.log('创建销售前检查Token是否存在:', !!token);
    
    console.log('创建销售请求数据:', JSON.stringify(saleData, null, 2));
    const response = await api.post('/sales', saleData);
    console.log('创建销售成功:', response.data);
    return response.data;
  } catch (error) {
    console.error('创建销售详细错误:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
      request: error.request ? '请求已发送' : '请求未发送'
    });
    
    // 特别处理401错误，可能是token刷新问题
    if (error.response && error.response.status === 401) {
      console.warn('创建销售时收到401未授权响应，可能是Token已过期');
      
      // 检查并打印详细的认证信息以便调试
      const authHeader = error.config?.headers?.Authorization;
      console.log('请求中的认证头:', authHeader ? '已设置' : '未设置');
      
      // 尝试读取服务器返回的详细错误信息
      const serverMessage = error.response.data?.error || error.response.data?.message;
      console.log('服务器返回的错误消息:', serverMessage);
    }
    
    handleApiError(error, '创建销售记录失败');
  }
};

export const refundSale = async (id) => {
  try {
    console.log(`处理退款 ID:${id}`);
    const response = await api.post(`/sales/${id}/refund`);
    console.log('退款处理成功:', response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, '退款处理失败');
  }
};

/**
 * 统一的API错误处理
 * @param {Error} error Axios错误对象
 * @param {string} defaultMessage 默认错误信息
 */
function handleApiError(error, defaultMessage) {
  console.group('API错误处理');
  console.error('原始错误:', error);
  
  if (error.response) {
    // 获取后端返回的 error 字段
    console.log('服务器返回了错误响应:', error.response.status, error.response.statusText);
    console.log('响应数据:', error.response.data);
    
    const errData = error.response.data.error;
    let message = defaultMessage;

    if (typeof errData === 'string') {
      message = errData;
    } else if (errData && typeof errData === 'object') {
      // 取第一个字段的第一个错误
      const key = Object.keys(errData)[0];
      const val = errData[key];
      if (Array.isArray(val)) {
        message = val[0];
      } else if (typeof val === 'string') {
        message = val;
      } else {
        message = JSON.stringify(errData);
      }
    }

    if (error.response.status === 401) {
      console.error('认证失败：需要重新登录');
      throw new Error('会话已过期，请重新登录');
    } else if (error.response.status === 403) {
      console.error('权限不足');
      throw new Error('您没有执行此操作的权限');
    }
    
    console.error('最终错误消息:', message);
    console.groupEnd();
    throw new Error(message);
  } else if (error.request) {
    // 请求已发送但没有收到响应
    console.error('请求已发送但没有收到响应');
    console.groupEnd();
    throw new Error('无法连接到服务器，请检查网络连接');
  } else {
    // 设置请求时发生的错误
    console.error('请求配置错误:', error.message);
    console.groupEnd();
    throw new Error(`发送请求时出错: ${error.message}`);
  }
}