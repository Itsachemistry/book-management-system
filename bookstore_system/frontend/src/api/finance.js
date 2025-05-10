import api from './index';

/**
 * 获取交易记录列表
 * @param {Object} params 查询参数 (start_date, end_date, transaction_type, page, per_page)
 * @returns {Promise<Object>} 交易记录列表和分页信息
 */
export const getTransactions = async (params = {}) => {
  try {
    const response = await api.get('/finance/transactions', { params });
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
    console.log('发送财务摘要请求:', params);
    // 确保API路径与后端匹配
    const response = await api.get('/finance/summary', { params });
    console.log('财务摘要API响应:', response.data);
    return response.data;
  } catch (error) {
    console.error('获取财务摘要API错误:', error);
    // 捕获并提供详细错误信息
    if (error.response) {
      console.error('错误响应状态码:', error.response.status);
      console.error('错误响应数据:', error.response.data);
    }
    throw handleError(error, '获取财务摘要失败');
  }
};

/**
 * 获取财务趋势数据
 * @param {Object} params 查询参数 (period: 'daily'|'weekly'|'monthly', limit, start_date, end_date)
 * @returns {Promise<Array>} 财务趋势数据
 */
export const getFinanceTrend = async (params = {}) => {
  try {
    const response = await api.get('/finance/reports/sales-trend', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取财务趋势数据失败');
  }
};

/**
 * 获取销售统计数据
 * @param {Object} params 查询参数 (start_date, end_date)
 * @returns {Promise<Object>} 销售统计数据
 */
export const getSalesStatistics = async (params = {}) => {
  try {
    const response = await api.get('/finance/reports/sales-statistics', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取销售统计数据失败');
  }
};

/**
 * 获取畅销书籍排行榜
 * @param {Object} params 查询参数 (start_date, end_date, limit)
 * @returns {Promise<Array>} 畅销书籍数据
 */
export const getTopSellingBooks = async (params = {}) => {
  try {
    const response = await api.get('/finance/reports/top-selling-books', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取畅销书籍排行榜失败');
  }
};

/**
 * 获取利润分析数据
 * @param {Object} params 查询参数 (start_date, end_date)
 * @returns {Promise<Object>} 利润分析数据
 */
export const getProfitAnalysis = async (params = {}) => {
  try {
    const response = await api.get('/finance/reports/profit-analysis', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取利润分析数据失败');
  }
};

/**
 * 获取按分类的收入报表
 * @param {Object} params 查询参数 (start_date, end_date)
 * @returns {Promise<Array>} 分类收入数据
 */
export const getRevenueByCategory = async (params = {}) => {
  try {
    const response = await api.get('/finance/reports/revenue-by-category', { params });
    return response.data;
  } catch (error) {
    throw handleError(error, '获取分类收入报表失败');
  }
};

/**
 * 导出财务报表数据
 * @param {String} reportType 报表类型 ('transactions', 'sales', 'profit')
 * @param {Object} params 查询参数 (start_date, end_date, format: 'csv'|'excel')
 * @returns {Promise<Blob>} 报表数据文件
 */
export const exportFinanceReport = async (reportType, params = {}) => {
  try {
    const response = await api.get(`/finance/export/${reportType}`, { 
      params,
      responseType: 'blob' 
    });
    return response.data;
  } catch (error) {
    throw handleError(error, '导出报表数据失败');
  }
};

/**
 * 处理API错误
 */
function handleError(error, defaultMessage) {
  console.error(`${defaultMessage}:`, error);
  
  if (error.response && error.response.data) {
    if (error.response.data.error) {
      throw new Error(error.response.data.error);
    }
  }
  
  throw new Error(defaultMessage || '操作失败');
}