<template>
  <div class="export-button">
    <button 
      class="export-btn" 
      @click="toggleDropdown"
      :disabled="disabled"
    >
      导出
      <span class="dropdown-icon">▼</span>
    </button>
    <div v-if="showDropdown" class="dropdown-menu">
      <div class="dropdown-item" @click="exportAs('excel')">
        <span class="item-icon excel">📊</span>
        导出为Excel
      </div>
      <div class="dropdown-item" @click="exportAs('csv')">
        <span class="item-icon csv">📄</span>
        导出为CSV
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// 属性
const props = defineProps({
  reportType: {
    type: String,
    default: 'transactions'
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

// 事件
const emit = defineEmits(['export']);

// 状态
const showDropdown = ref(false);

// 切换下拉菜单
const toggleDropdown = () => {
  if (props.disabled) return;
  showDropdown.value = !showDropdown.value;
};

// 导出为指定格式
const exportAs = (format) => {
  emit('export', { format, reportType: props.reportType });
  showDropdown.value = false;
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  const exportBtn = event.target.closest('.export-button');
  if (!exportBtn) {
    showDropdown.value = false;
  }
};

// 添加/移除事件监听器
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.export-button {
  position: relative;
}

.export-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.export-btn:hover {
  background-color: #40a9ff;
}

.export-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.dropdown-icon {
  margin-left: 8px;
  font-size: 10px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 100;
  min-width: 150px;
  margin-top: 4px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.item-icon {
  margin-right: 8px;
}
</style>
