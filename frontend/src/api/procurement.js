import api from './index';

/**
 * 获取进货订单列表
 * @param {Object} params 查询参数 (status, start_date, end_date, page, per_page等)
 * @returns {Promise} 订单列表和分页信息
 */
export const getOrders = async (params = {}) => {
  const response = await api.get('/api/procurement/orders', { params });
  return response.data;
};

/**
 * 获取单个订单详情
 * @param {Number} id 订单ID
 * @returns {Promise} 订单详细信息
 */
export const getOrder = async (id) => {
  const response = await api.get(`/api/procurement/orders/${id}`);
  return response.data;
};

/**
 * 创建新的进货订单
 * @param {Object} data 订单数据 (supplier, remarks, items等)
 * @returns {Promise} 创建的订单
 */
export const createOrder = async (data) => {
  const response = await api.post('/api/procurement/orders', data);
  return response.data;
};

/**
 * 更新订单信息
 * @param {Number} id 订单ID
 * @param {Object} data 要更新的数据 (supplier, remarks等)
 * @returns {Promise} 更新后的订单
 */
export const updateOrder = async (id, data) => {
  const response = await api.put(`/api/procurement/orders/${id}`, data);
  return response.data;
};

/**
 * 支付订单
 * @param {Number} id 订单ID
 * @returns {Promise} 处理结果
 */
export const payOrder = async (id) => {
  const response = await api.post(`/api/procurement/orders/${id}/pay`);
  return response.data;
};

/**
 * 退货订单
 * @param {Number} id 订单ID
 * @returns {Promise} 处理结果
 */
export const returnOrder = async (id) => {
  const response = await api.post(`/api/procurement/orders/${id}/return`);
  return response.data;
};

/**
 * 入库订单
 * @param {Number} id 订单ID
 * @returns {Promise} 处理结果
 */
export const stockInOrder = async (id) => {
  const response = await api.post(`/api/procurement/orders/${id}/stock-in`);
  return response.data;
};