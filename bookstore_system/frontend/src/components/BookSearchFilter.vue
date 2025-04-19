<template>
  <div class="search-filter">
    <div class="search-bar">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="搜索书籍名称、作者或ISBN..."
        @input="onSearchInput"
      />
      <button class="search-button" @click="onSearch">
        <span class="search-icon">🔍</span>
      </button>
    </div>
    
    <div class="filters">
      <label class="filter-checkbox">
        <input 
          type="checkbox"
          v-model="onlyActive"
          @change="onFilterChange"
        />
        只显示可用书籍
      </label>
      
      <div class="per-page-selector">
        <span>每页显示：</span>
        <select v-model="perPage" @change="onPerPageChange">
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps, watch } from 'vue';
import { debounce } from 'lodash';

// 定义属性
const props = defineProps({
  initialSearch: {
    type: String,
    default: ''
  },
  initialPerPage: {
    type: Number,
    default: 20
  },
  initialActiveOnly: {
    type: Boolean,
    default: true
  }
});

// 定义状态
const searchQuery = ref(props.initialSearch);
const perPage = ref(props.initialPerPage);
const onlyActive = ref(props.initialActiveOnly);

// 定义事件
const emit = defineEmits(['search', 'filter-change', 'per-page-change']);

// 定义防抖搜索函数，避免频繁触发搜索
const debouncedSearch = debounce(() => {
  emit('search', searchQuery.value);
}, 300);

// 监听搜索输入
function onSearchInput() {
  debouncedSearch();
}

// 点击搜索按钮
function onSearch() {
  emit('search', searchQuery.value);
}

// 过滤条件变化
function onFilterChange() {
  emit('filter-change', { active_only: onlyActive.value });
}

// 每页数量变化
function onPerPageChange() {
  emit('per-page-change', parseInt(perPage.value));
}

// 监听属性变化，同步到内部状态
watch(() => props.initialSearch, (newVal) => {
  searchQuery.value = newVal;
});

watch(() => props.initialPerPage, (newVal) => {
  perPage.value = newVal;
});

watch(() => props.initialActiveOnly, (newVal) => {
  onlyActive.value = newVal;
});
</script>

<style scoped>
.search-filter {
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  margin-bottom: 10px;
}

.search-bar input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-button {
  padding: 8px 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.search-icon {
  font-size: 16px;
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.filter-checkbox input {
  margin-right: 5px;
}

.per-page-selector {
  display: flex;
  align-items: center;
}

.per-page-selector span {
  margin-right: 5px;
}

.per-page-selector select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>