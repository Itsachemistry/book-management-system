import api from './index';

/**
 * 获取交易记录列表
 * @param {Object} params 查询参数 (start_date, end_date, transaction_type, page, per_page)
 * @returns {Promise<Object>} 交易记录列表和分页信息
 */
export const getTransactions = async (params = {}) => {
  try {
    const response = await api.get('/api/finance/transactions', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取交易记录失败');
  }
};

/**
 * 获取财务摘要
 * @param {Object} params 查询参数 (start_date, end_date)
 * @returns {Promise<Object>} 财务摘要数据
 */
export const getFinanceSummary = async (params = {}) => {
  try {
    const response = await api.get('/api/finance/summary', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取财务摘要失败');
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