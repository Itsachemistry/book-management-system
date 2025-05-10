<template>
  <div class="finance-trend-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="period-selector">
        <button 
          v-for="option in periodOptions" 
          :key="option.value"
          :class="['period-btn', { active: currentPeriod === option.value }]"
          @click="changePeriod(option.value)"
        >
          {{ option.label }}
        </button>
      </div>
    </div>
    <div class="chart-container" ref="chartContainer"></div>
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>加载图表数据中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  // 图表标题
  title: {
    type: String,
    default: '财务趋势'
  },
  // 图表数据
  chartData: {
    type: Object,
    default: () => ({
      dates: [],
      income: [],
      expense: [],
      profit: []
    })
  },
  // 初始周期
  initialPeriod: {
    type: String,
    default: 'monthly'
  },
  // 是否正在加载
  loading: {
    type: Boolean,
    default: false
  }
});

// 事件
const emit = defineEmits(['period-change']);

// 状态变量
const chartContainer = ref(null);
const chartInstance = ref(null);
const currentPeriod = ref(props.initialPeriod);

// 周期选项
const periodOptions = [
  { label: '日', value: 'daily' },
  { label: '周', value: 'weekly' },
  { label: '月', value: 'monthly' }
];

// 切换周期
const changePeriod = (period) => {
  currentPeriod.value = period;
  emit('period-change', period);
};

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return;
  
  chartInstance.value = echarts.init(chartContainer.value);
  updateChart();
};

// 处理窗口大小变化
const handleResize = () => {
  chartInstance.value?.resize();
};

// 更新图表
const updateChart = () => {
  if (!chartInstance.value) return;
  
  const { dates, income, expense, profit } = props.chartData;
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        let tooltip = params[0].name + '<br/>';
        params.forEach(item => {
          const color = item.color;
          const value = item.value === undefined ? '-' : '¥' + item.value.toFixed(2);
          tooltip += `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${color};margin-right:5px;"></span>${item.seriesName}: ${value}<br/>`;
        });
        return tooltip;
      }
    },
    legend: {
      data: ['收入', '支出', '利润'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '60px',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates || [],
      axisLabel: {
        interval: 0,
        rotate: 30,
        formatter: function(value) {
          // 根据周期格式化时间标签
          if (currentPeriod.value === 'monthly') {
            return value.substring(0, 7); // YYYY-MM
          } else if (currentPeriod.value === 'weekly') {
            return value; // 周标签通常已格式化
          } else {
            return value; // YYYY-MM-DD
          }
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        stack: 'total',
        itemStyle: {
          color: '#52c41a'
        },
        data: income || []
      },
      {
        name: '支出',
        type: 'bar',
        stack: 'total',
        itemStyle: {
          color: '#ff4d4f'
        },
        data: expense || []
      },
      {
        name: '利润',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#1890ff'
        },
        data: profit || []
      }
    ]
  };
  
  chartInstance.value.setOption(option);
};

// 监听数据变化
watch(
  () => props.chartData,
  () => {
    updateChart();
  },
  { deep: true }
);

// 监听loading状态
watch(
  () => props.loading,
  (newValue) => {
    if (!chartInstance.value) return;
    
    if (newValue) {
      chartInstance.value.showLoading({
        text: '加载中...',
        maskColor: 'rgba(255, 255, 255, 0.8)'
      });
    } else {
      chartInstance.value.hideLoading();
    }
  }
);

// 组件挂载和卸载
onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.finance-trend-chart {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-header h3 {
  margin: 0;
  font-weight: 500;
}

.period-selector {
  display: flex;
  gap: 5px;
}

.period-btn {
  padding: 4px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f5f5f5;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.period-btn.active {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
