import api from './index';

/**
 * 获取进货订单列表
 * @param {Object} params 查询参数 (status, start_date, end_date, page, per_page)
 * @returns {Promise} 返回订单列表和分页信息
 */
export const getOrders = async (params = {}) => {
  try {
    const response = await api.get('/procurement/orders', { params });
    return response.data;
  } catch (error) {
    console.error('获取进货订单列表失败:', error);
    throw error;
  }
};

/**
 * 获取单个进货订单详情
 * @param {number} id 订单ID
 * @returns {Promise} 返回订单详情
 */
export const getOrder = async (id) => {
  try {
    const response = await api.get(`/procurement/orders/${id}`);
    return response.data;
  } catch (error) {
    console.error('获取订单详情失败:', error);
    throw error;
  }
};

/**
 * 创建新的进货订单
 * @param {Object} orderData 订单数据
 * @returns {Promise} 返回创建的订单
 */
export const createOrder = async (orderData) => {
  try {
    const response = await api.post('/procurement/orders', orderData);
    return response.data;
  } catch (error) {
    console.error('创建订单失败:', error);
    throw error;
  }
};

/**
 * 更新进货订单基本信息
 * @param {number} id 订单ID
 * @param {Object} orderData 要更新的数据
 * @returns {Promise} 返回更新后的订单
 */
export const updateOrder = async (id, orderData) => {
  try {
    const response = await api.put(`/procurement/orders/${id}`, orderData);
    return response.data;
  } catch (error) {
    console.error('更新订单失败:', error);
    throw error;
  }
};

/**
 * 支付进货订单
 * @param {number} id 订单ID
 * @returns {Promise} 返回操作结果
 */
export const payOrder = async (id) => {
  try {
    const response = await api.post(`/procurement/orders/${id}/pay`);
    return response.data;
  } catch (error) {
    console.error('支付订单失败:', error);
    throw error;
  }
};

/**
 * 退货进货订单
 * @param {number} id 订单ID
 * @returns {Promise} 返回操作结果
 */
export const returnOrder = async (id) => {
  try {
    const response = await api.post(`/procurement/orders/${id}/return`);
    return response.data;
  } catch (error) {
    console.error('退货订单失败:', error);
    throw error;
  }
};

/**
 * 入库进货订单
 * @param {number} id 订单ID
 * @returns {Promise} 返回操作结果
 */
export const stockInOrder = async (id) => {
  try {
    const response = await api.post(`/procurement/orders/${id}/stock-in`);
    return response.data;
  } catch (error) {
    console.error('入库操作失败:', error);
    throw error;
  }
};