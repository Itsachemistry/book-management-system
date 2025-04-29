import apiClient from './index.js';

/**
 * 获取图书列表
 * @param {Object} params 查询参数 { active_only, per_page, page, ... }
 * @returns {Promise<Object>} 包含图书列表和分页信息的对象
 */
export async function getBooks(params = {}) {
  console.log('开始获取图书列表, 参数:', params);
  try {
    // 记录请求前状态
    console.log('准备发送GET请求到/books/');
    
    const response = await apiClient.get('/books/', { params });
    
    // 记录请求成功状态
    console.log('获取图书列表成功:', response.status, response.statusText);
    console.log('获取到图书数量:', response.data.items ? response.data.items.length : 0);
    
    return response.data;
  } catch (error) {
    console.error('获取图书列表详细错误:', {
      message: error.message,
      config: error.config,
      response: error.response ? {
        status: error.response.status,
        data: error.response.data
      } : '无响应',
      code: error.code,
      isAxiosError: error.isAxiosError
    });
    
    handleApiError(error, '获取图书列表失败');
  }
}

/**
 * 获取单本书籍详情
 * @param {string|number} id 书籍ID或ISBN
 * @returns {Promise<Object>} 书籍信息
 */
export async function getBook(id) {
  try {
    const response = await apiClient.get(`/books/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error, '获取书籍详情失败');
  }
}

/**
 * 创建新书籍
 * @param {Object} bookData 书籍数据
 * @returns {Promise<Object>} 创建的书籍信息
 */
export async function createBook(bookData) {
  try {
    // 数据预处理：确保数值类型字段为数字，并移除is_active字段
    const processedData = {
      isbn: bookData.isbn,
      name: bookData.name,
      author: bookData.author || '',
      publisher: bookData.publisher || '',
      retail_price: Number(bookData.retail_price),
      quantity: Number(bookData.quantity)
      // 注意：这里不包含is_active字段
    };
    
    // 打印请求数据，帮助调试
    console.log('创建书籍请求数据:', {
      请求URL: `${apiClient.defaults.baseURL}/books`,
      数据: processedData
    });
    
    const response = await apiClient.post('/books', processedData);
    console.log('创建书籍成功响应:', response.data);
    return response.data;
  } catch (error) {
    console.error('创建书籍失败:', error);
    
    // 更详细的错误处理
    if (error.response) {
      const { status, data } = error.response;
      console.error(`服务器返回 ${status} 错误:`, data);
      
      // 处理常见错误情况
      if (status === 400) {
        if (data.error) {
          if (typeof data.error === 'string') {
            throw new Error(`验证错误: ${data.error}`);
          } else if (typeof data.error === 'object') {
            // 格式化对象错误消息
            const errorMessages = Object.entries(data.error)
              .map(([field, errors]) => {
                if (Array.isArray(errors)) return `${field}: ${errors.join(', ')}`;
                return `${field}: ${errors}`;
              })
              .join('; ');
            throw new Error(`表单验证失败: ${errorMessages}`);
          }
        }
      } 
      
      // 默认错误消息
      throw new Error(data.error || '添加书籍失败，请稍后重试');
    }
    
    // 网络或其他错误
    throw new Error('无法连接服务器或网络错误');
  }
}

/**
 * 更新书籍信息
 * @param {number} id 书籍ID
 * @param {Object} bookData 书籍数据
 * @returns {Promise<Object>} 更新后的书籍信息
 */
export async function updateBook(id, bookData) {
  try {
    // 数据预处理：确保所有字段使用正确的类型，移除isbn字段
    const processedData = {
      name: bookData.name,
      author: bookData.author || '',
      publisher: bookData.publisher || '',
      retail_price: Number(bookData.retail_price),  // 转为数字
      quantity: Number(bookData.quantity),          // 转为数字
      is_active: Boolean(bookData.is_active)        // 显式转换为布尔值
    };
    
    console.log('更新书籍请求数据:', {
      请求URL: `${apiClient.defaults.baseURL}/books/${id}`,
      数据: processedData
    });
    
    const response = await apiClient.put(`/books/${id}`, processedData);
    return response.data;
  } catch (error) {
    handleApiError(error, '更新书籍失败');
  }
}

/**
 * 删除书籍（逻辑删除）
 * @param {number} id 书籍ID
 * @returns {Promise<Object>} 响应信息
 */
export async function deleteBook(id) {
  try {
    const response = await apiClient.delete(`/books/${id}`);
    return response.data;
  } catch (error) {
    handleApiError(error, '删除书籍失败');
  }
}

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

