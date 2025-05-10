<template>
  <div class="bulk-import-view">
    <h1>批量导入图书</h1>
    
    <!-- 步骤指示器 -->
    <div class="step-indicator">
      <div class="step" :class="{ 'active': currentStep === 1 }">1. 上传文件</div>
      <div class="step" :class="{ 'active': currentStep === 2 }">2. 映射字段</div>
      <div class="step" :class="{ 'active': currentStep === 3 }">3. 预览数据</div>
      <div class="step" :class="{ 'active': currentStep === 4 }">4. 导入结果</div>
    </div>
    
    <!-- 步骤1: 文件上传 -->
    <div v-if="currentStep === 1" class="step-content">
      <h2>上传文件</h2>
      <div class="file-upload-container">
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleFileUpload" 
          accept=".csv, .xlsx, .xls"
        >
        <div class="upload-instructions">
          <p>支持的文件格式: CSV, Excel (.xlsx, .xls)</p>
          <p>文件应包含图书数据，每行一条记录</p>
        </div>
      </div>
      <div v-if="uploadError" class="error-message">{{ uploadError }}</div>
      <button class="btn btn-primary" @click="currentStep = 2" :disabled="!parsedData.length">
        下一步
      </button>
    </div>
    
    <!-- 步骤2: 字段映射 -->
    <div v-if="currentStep === 2" class="step-content">
      <h2>映射字段</h2>
      <p>请将导入文件中的列映射到系统字段</p>
      
      <table class="mapping-table">
        <thead>
          <tr>
            <th>系统字段</th>
            <th>文件列</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="field in requiredFields" :key="field.key">
            <td>{{ field.label }} {{ field.required ? '*' : '' }}</td>
            <td>
              <select v-model="fieldMapping[field.key]">
                <option value="">-- 请选择 --</option>
                <option v-for="column in fileColumns" :key="column" :value="column">
                  {{ column }}
                </option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div class="form-actions">
        <button class="btn btn-secondary" @click="currentStep = 1">上一步</button>
        <button class="btn btn-primary" @click="validateMappingAndContinue" :disabled="!isMappingValid">
          下一步
        </button>
      </div>
    </div>
    
    <!-- 步骤3: 预览数据 -->
    <div v-if="currentStep === 3" class="step-content">
      <h2>数据预览</h2>
      <p>请确认以下数据是否正确</p>
      
      <div class="preview-container">
        <table class="preview-table">
          <thead>
            <tr>
              <th v-for="field in requiredFields" :key="field.key">
                {{ field.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in previewData" :key="index">
              <td v-for="field in requiredFields" :key="field.key">
                {{ item[field.key] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="form-actions">
        <button class="btn btn-secondary" @click="currentStep = 2">上一步</button>
        <button class="btn btn-primary" @click="importBooks" :disabled="importing">
          {{ importing ? '导入中...' : '开始导入' }}
        </button>
      </div>
    </div>
    
    <!-- 步骤4: 导入结果 -->
    <div v-if="currentStep === 4" class="step-content">
      <h2>导入结果</h2>
      
      <div class="import-summary">
        <div class="summary-item success">
          <div class="count">{{ importResults.success }}</div>
          <div class="label">成功导入</div>
        </div>
        <div class="summary-item failure">
          <div class="count">{{ importResults.failed }}</div>
          <div class="label">导入失败</div>
        </div>
      </div>
      
      <div v-if="importResults.errors.length > 0" class="error-list">
        <h3>导入错误列表</h3>
        <table>
          <thead>
            <tr>
              <th>ISBN</th>
              <th>书名</th>
              <th>错误信息</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(error, index) in importResults.errors" :key="index">
              <td>{{ error.isbn }}</td>
              <td>{{ error.name }}</td>
              <td>{{ error.error }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="form-actions">
        <button class="btn btn-primary" @click="currentStep = 1">开始新导入</button>
        <button class="btn btn-secondary" @click="$router.push('/books')">返回图书库存</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue';
import Papa from 'papaparse'; // CSV解析库
import { useBookStore } from '../store/book';
import * as XLSX from 'xlsx'; // Excel解析库

export default {
  name: 'BulkImportView',
  setup() {
    const bookStore = useBookStore();
    const currentStep = ref(1);
    const fileInput = ref(null);
    const parsedData = ref([]);
    const fileColumns = ref([]);
    const uploadError = ref('');
    const importing = ref(false);
    const importResults = ref({
      success: 0,
      failed: 0,
      errors: []
    });
    
    // 系统要求的字段
    const requiredFields = [
      { key: 'isbn', label: 'ISBN', required: true },
      { key: 'name', label: '书名', required: true },
      { key: 'author', label: '作者', required: false },
      { key: 'publisher', label: '出版社', required: false },
      { key: 'retail_price', label: '售价', required: true },
      { key: 'quantity', label: '库存数量', required: true }
    ];
    
    // 字段映射
    const fieldMapping = reactive({});
    
    // 处理文件上传
    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      uploadError.value = '';
      
      // 判断文件类型并解析
      if (file.name.endsWith('.csv')) {
        parseCSV(file);
      } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        parseExcel(file);
      } else {
        uploadError.value = '不支持的文件格式';
      }
    };
    
    // 解析CSV文件
    const parseCSV = (file) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.data && results.data.length > 0) {
            parsedData.value = results.data;
            fileColumns.value = results.meta.fields;
            // 自动映射同名或相似字段
            autoMapFields();
          } else {
            uploadError.value = '文件中没有找到数据';
          }
        },
        error: (error) => {
          uploadError.value = `解析CSV文件失败: ${error.message}`;
        }
      });
    };
    
    // 解析Excel文件
    const parseExcel = (file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target.result;
          const workbook = XLSX.read(data, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          
          if (jsonData && jsonData.length > 0) {
            parsedData.value = jsonData;
            fileColumns.value = Object.keys(jsonData[0]);
            // 自动映射同名或相似字段
            autoMapFields();
          } else {
            uploadError.value = '文件中没有找到数据';
          }
        } catch (error) {
          uploadError.value = `解析Excel文件失败: ${error.message}`;
        }
      };
      reader.readAsArrayBuffer(file);
    };
    
    // 自动字段映射
    const autoMapFields = () => {
      // 映射规则 - 根据中文名和字段名映射
      const mappingRules = {
        'isbn': ['isbn', 'ISBN', '书号'],
        'name': ['name', '书名', '标题', 'title'],
        'author': ['author', '作者'],
        'publisher': ['publisher', '出版社'],
        'retail_price': ['retail_price', '售价', '价格', 'price'],
        'quantity': ['quantity', '库存', '库存数量']
      };
      
      requiredFields.forEach(field => {
        const possibleNames = mappingRules[field.key] || [field.key];
        const match = fileColumns.value.find(column => 
          possibleNames.some(name => 
            column.toLowerCase() === name.toLowerCase() || 
            column.includes(name)
          )
        );
        
        if (match) {
          fieldMapping[field.key] = match;
        }
      });
    };
    
    // 检查映射是否有效
    const isMappingValid = computed(() => {
      return requiredFields
        .filter(field => field.required)
        .every(field => fieldMapping[field.key]);
    });
    
    // 验证映射并继续
    const validateMappingAndContinue = () => {
      if (isMappingValid.value) {
        preparePreviewData();
        currentStep.value = 3;
      }
    };
    
    // 预处理预览数据
    const previewData = ref([]);
    const preparePreviewData = () => {
      // 转换数据结构以匹配系统字段
      previewData.value = parsedData.value.slice(0, 10).map(item => {
        const transformed = {};
        requiredFields.forEach(field => {
          if (fieldMapping[field.key]) {
            let value = item[fieldMapping[field.key]];
            
            // 数据类型转换
            if (field.key === 'retail_price') {
              value = parseFloat(value) || 0;
            } else if (field.key === 'quantity') {
              value = parseInt(value) || 0;
            }
            
            transformed[field.key] = value;
          }
        });
        return transformed;
      });
    };
    
    // 批量导入书籍
    const importBooks = async () => {
      importing.value = true;
      importResults.value = {
        success: 0,
        failed: 0,
        errors: []
      };
      
      try {
        // 转换所有数据
        const booksToImport = parsedData.value.map(item => {
          const bookData = {};
          requiredFields.forEach(field => {
            if (fieldMapping[field.key]) {
              let value = item[fieldMapping[field.key]];
              
              // 数据类型转换
              if (field.key === 'retail_price') {
                value = parseFloat(value) || 0;
              } else if (field.key === 'quantity') {
                value = parseInt(value) || 0;
              }
              
              bookData[field.key] = value;
            }
          });
          return bookData;
        });
        
        // 分批导入，每批10本
        const batchSize = 10;
        for (let i = 0; i < booksToImport.length; i += batchSize) {
          const batch = booksToImport.slice(i, i + batchSize);
          
          // 串行处理每一本书
          for (const book of batch) {
            try {
              await bookStore.addBook(book);
              importResults.value.success++;
            } catch (error) {
              importResults.value.failed++;
              importResults.value.errors.push({
                isbn: book.isbn,
                name: book.name,
                error: error.message
              });
            }
          }
        }
      } catch (error) {
        console.error('批量导入失败:', error);
      } finally {
        importing.value = false;
        currentStep.value = 4;
      }
    };
    
    return {
      currentStep,
      fileInput,
      parsedData,
      fileColumns,
      uploadError,
      requiredFields,
      fieldMapping,
      isMappingValid,
      importing,
      previewData,
      importResults,
      handleFileUpload,
      validateMappingAndContinue,
      importBooks
    };
  }
};
</script>

<style scoped>
.bulk-import-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
h1 {
    color: #2c3e50;
    margin-bottom: 20px;
}

.action-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    border: none;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    text-decoration: none;
}

.btn i {
    margin-right: 6px;
}

.btn-primary {
    background-color: #4CAF50;
    color: white;
}

.btn-secondary {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
}

.btn-secondary:hover {
    background-color: #e8e8e8;
}
.step-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.step {
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  flex: 1;
  margin: 0 5px;
  text-align: center;
  color: #666;
}

.step.active {
  background-color: #4CAF50;
  color: white;
  font-weight: bold;
}

.step-content {
  margin-top: 20px;
}

.file-upload-container {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
  margin: 20px 0;
  border-radius: 5px;
}

.upload-instructions {
  margin-top: 15px;
  color: #666;
}

.error-message {
  color: #f44336;
  margin: 10px 0;
}

.mapping-table, .preview-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.mapping-table th, .mapping-table td,
.preview-table th, .preview-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}

.mapping-table select {
  width: 100%;
  padding: 8px;
}

.preview-container {
  max-height: 400px;
  overflow-y: auto;
  margin: 20px 0;
  border: 1px solid #eee;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}

.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.import-summary {
  display: flex;
  justify-content: center;
  margin: 30px 0;
}

.summary-item {
  text-align: center;
  padding: 20px;
  margin: 0 15px;
  border-radius: 10px;
  width: 150px;
}

.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.failure {
  background-color: #ffebee;
  color: #c62828;
}

.count {
  font-size: 48px;
  font-weight: bold;
}

.label {
  margin-top: 10px;
  font-size: 16px;
}

.error-list {
  margin-top: 30px;
}

.error-list table {
  width: 100%;
  border-collapse: collapse;
}

.error-list th, .error-list td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}

.error-list th {
  background-color: #f5f5f5;
}
</style>