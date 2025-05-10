<template>
  <div class="date-range-picker">
    <div class="date-field">
      <label>开始日期：</label>
      <input type="date" v-model="startDateModel" class="date-input" />
    </div>
    <div class="date-field">
      <label>结束日期：</label>
      <input type="date" v-model="endDateModel" class="date-input" />
    </div>
    <div class="quick-selectors">
      <button class="quick-btn" @click="selectLastWeek">上周</button>
      <button class="quick-btn" @click="selectLastMonth">上月</button>
      <button class="quick-btn" @click="selectCurrentMonth">本月</button>
      <button class="quick-btn" @click="selectThisYear">今年</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

// 接收属性
const props = defineProps({
  startDate: {
    type: String,
    default: ''
  },
  endDate: {
    type: String,
    default: ''
  }
});

// 定义事件
const emit = defineEmits(['change']);

// 本地状态
const startDateModel = ref(props.startDate);
const endDateModel = ref(props.endDate);

// 监听props变化
watch(() => props.startDate, (newVal) => {
  startDateModel.value = newVal;
});

watch(() => props.endDate, (newVal) => {
  endDateModel.value = newVal;
});

// 监听本地状态变化
watch([startDateModel, endDateModel], ([newStart, newEnd]) => {
  emit('change', {
    startDate: newStart,
    endDate: newEnd
  });
}, { deep: true });

// 日期选择方法
const selectLastWeek = () => {
  const today = new Date();
  const lastWeekStart = new Date(today);
  lastWeekStart.setDate(today.getDate() - 7);
  
  startDateModel.value = formatDate(lastWeekStart);
  endDateModel.value = formatDate(today);
};

const selectLastMonth = () => {
  const today = new Date();
  const lastMonth = new Date(today);
  lastMonth.setMonth(today.getMonth() - 1);
  
  startDateModel.value = formatDate(lastMonth);
  endDateModel.value = formatDate(today);
};

const selectCurrentMonth = () => {
  const today = new Date();
  const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  
  startDateModel.value = formatDate(firstDayOfMonth);
  endDateModel.value = formatDate(today);
};

const selectThisYear = () => {
  const today = new Date();
  const firstDayOfYear = new Date(today.getFullYear(), 0, 1);
  
  startDateModel.value = formatDate(firstDayOfYear);
  endDateModel.value = formatDate(today);
};

// 格式化日期为YYYY-MM-DD
const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};
</script>

<style scoped>
.date-range-picker {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
}

.date-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  transition: all 0.3s;
}

.date-input:focus {
  outline: none;
  border-color: #40a9ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.quick-selectors {
  display: flex;
  gap: 5px;
}

.quick-btn {
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background-color: #f5f5f5;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn:hover {
  color: #40a9ff;
  border-color: #40a9ff;
}

@media (max-width: 768px) {
  .date-range-picker {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .date-field {
    width: 100%;
  }
  
  .quick-selectors {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
