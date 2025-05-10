<template>
  <div class="transaction-type-filter">
    <label>交易类型：</label>
    <div class="filter-buttons">
      <button 
        v-for="option in options" 
        :key="option.value"
        :class="['filter-btn', { active: selectedType === option.value }]"
        @click="selectType(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  initialValue: {
    type: String,
    default: 'ALL'
  }
});

const emit = defineEmits(['change']);

// 过滤器选项
const options = [
  { label: '全部', value: 'ALL' },
  { label: '收入', value: 'INCOME' },
  { label: '支出', value: 'EXPENSE' }
];

// 当前选中的类型
const selectedType = ref(props.initialValue);

// 选择类型
const selectType = (type) => {
  selectedType.value = type;
  emit('change', type);
};
</script>

<style scoped>
.transaction-type-filter {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

.filter-btn.active {
  background-color: #1890ff;
  border-color: #1890ff;
  color: white;
}
</style>
