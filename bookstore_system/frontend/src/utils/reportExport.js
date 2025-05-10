/**
 * 导出数据为CSV文件
 * @param {Array} data 要导出的数据
 * @param {Array} columns 列定义 [{title, dataKey}]
 * @param {String} filename 文件名（不含扩展名）
 */
export const exportToCsv = (data, columns, filename) => {
  // 生成列标题行
  const header = columns.map(column => `"${column.title}"`).join(',');
  
  // 生成数据行
  const rows = data.map(item => {
    return columns.map(column => {
      const value = item[column.dataKey];
      // 确保字符串值被正确地引用，避免CSV注入
      return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
    }).join(',');
  });
  
  // 合并所有行
  const csv = [header, ...rows].join('\n');
  
  // 创建Blob对象
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  
  downloadFile(blob, `${filename}.csv`);
};

/**
 * 导出数据为Excel文件（简易版）
 * @param {Array} data 要导出的数据
 * @param {Array} columns 列定义 [{title, dataKey}]
 * @param {String} filename 文件名（不含扩展名）
 * @param {String} sheetName 工作表名称
 */
export const exportToExcel = (data, columns, filename, sheetName = 'Sheet1') => {
  // 创建一个基本的Excel XML格式
  const xmlHeader = '<?xml version="1.0"?><?mso-application progid="Excel.Sheet"?>';
  const workbookStart = '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">';
  const workbookEnd = '</Workbook>';
  
  // 创建工作表
  let sheetContent = `<Worksheet ss:Name="${sheetName}"><Table>`;
  
  // 添加标题行
  sheetContent += '<Row>';
  columns.forEach(column => {
    sheetContent += `<Cell><Data ss:Type="String">${column.title}</Data></Cell>`;
  });
  sheetContent += '</Row>';
  
  // 添加数据行
  data.forEach(item => {
    sheetContent += '<Row>';
    columns.forEach(column => {
      const value = item[column.dataKey];
      const type = typeof value === 'number' ? 'Number' : 'String';
      sheetContent += `<Cell><Data ss:Type="${type}">${value}</Data></Cell>`;
    });
    sheetContent += '</Row>';
  });
  
  // 完成工作表
  sheetContent += '</Table></Worksheet>';
  
  // 组装完整的Excel文档
  const excelContent = `${xmlHeader}${workbookStart}${sheetContent}${workbookEnd}`;
  
  // 创建Blob对象
  const blob = new Blob([excelContent], { type: 'application/vnd.ms-excel' });
  
  downloadFile(blob, `${filename}.xls`);
};

/**
 * 格式化交易记录用于导出
 * @param {Array} transactions 交易记录
 * @returns {Object} 包含格式化后的数据和列定义
 */
export const formatTransactionsForExport = (transactions) => {
  // 定义导出的列
  const columns = [
    { title: '日期', dataKey: 'date' },
    { title: '交易类型', dataKey: 'type' },
    { title: '金额', dataKey: 'amount' },
    { title: '描述', dataKey: 'description' },
    { title: '参考订单', dataKey: 'reference' }
  ];
  
  // 格式化数据
  const data = transactions.map(transaction => {
    return {
      date: formatDate(transaction.date),
      type: getTransactionTypeText(transaction.transaction_type),
      amount: parseFloat(transaction.amount).toFixed(2),
      description: transaction.description || '',
      reference: transaction.reference_number || ''
    };
  });
  
  return { data, columns };
};

/**
 * 辅助函数：下载文件
 * @param {Blob} blob Blob对象
 * @param {String} filename 文件名
 */
const downloadFile = (blob, filename) => {
  // 创建下载链接
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  // 设置链接属性
  link.href = url;
  link.download = filename;
  
  // 触发点击以开始下载
  document.body.appendChild(link);
  link.click();
  
  // 清理
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * 辅助函数：格式化日期
 * @param {String} dateString 日期字符串
 * @returns {String} 格式化的日期
 */
const formatDate = (dateString) => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return dateString;
  }
};

/**
 * 辅助函数：获取交易类型文本
 * @param {String} type 交易类型代码
 * @returns {String} 交易类型文本
 */
const getTransactionTypeText = (type) => {
  const typeMap = {
    'INCOME': '收入',
    'EXPENSE': '支出'
  };
  return typeMap[type] || type;
};
