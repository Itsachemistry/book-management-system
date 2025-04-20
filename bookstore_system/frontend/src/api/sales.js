import api from './index';

/**
 * 创建销售记录
 * @param {Object} saleData 销售数据
 * @returns {Promise<Object>} 创建的销售记录
 */
export const createSale = async (saleData) => {
  try {
    const response = await api.post('/api/sales', saleData);
    return response.data;
  } catch (error) {
    throw handleError(error, '创建销售记录失败');
  }
};

/**
 * 获取销售记录列表
 * @param {Object} params 查询参数 (status, start_date, end_date, page, per_page)
 * @returns {Promise<Object>} 销售记录列表和分页信息
 */
export const getSales = async (params = {}) => {
  try {
    const response = await api.get('/api/sales', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取销售记录列表失败');
  }
};

/**
 * 获取单个销售记录详情
 * @param {number} id 销售记录ID
 * @returns {Promise<Object>} 销售记录详情
 */
export const getSale = async (id) => {
  try {
    const response = await api.get(`/api/sales/${id}`);
    return response.data;
  } catch (error) {
    throw handleError(error, '获取销售记录详情失败');
  }
};

/**
 * 退款处理
 * @param {number} id 销售记录ID
 * @returns {Promise<Object>} 退款结果
 */
export const refundSale = async (id) => {
  try {
    const response = await api.post(`/api/sales/${id}/refund`);
    return response.data;
  } catch (error) {
    throw handleError(error, '处理退款失败');
  }
};

/**
 * 处理API错误
 */
function handleError(error, defaultMessage) {
  if (error.response && error.response.data && error.response.data.error) {
    throw new Error(error.response.data.error);
  }
  throw new Error(defaultMessage || '操作失败');
}