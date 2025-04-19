import api from './index';

/**
 * 获取书籍列表
 * @param {Object} params 查询参数
 * @param {string} params.search 搜索关键词
 * @param {number} params.page 页码
 * @param {number} params.per_page 每页条数
 * @param {boolean} params.active_only 是否只返回有效书籍
 * @returns {Promise<Object>} 包含书籍列表和分页信息的对象
 */
export async function getBooks(params = {}) {
  try {
    const response = await api.get('/books/', { params });
    return response.data;
  } catch (error) {
    handleApiError(error, '获取书籍列表失败');
  }
}

/**
 * 获取单本书籍详情
 * @param {string|number} id 书籍ID或ISBN
 * @returns {Promise<Object>} 书籍信息
 */
export async function getBook(id) {
  try {
    const response = await api.get(`/books/${id}`);
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
    const response = await api.post('/books/', bookData);
    return response.data;
  } catch (error) {
    handleApiError(error, '创建书籍失败');
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
    const response = await api.put(`/books/${id}`, bookData);
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
    const response = await api.delete(`/books/${id}`);
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

