<template>
  <div class="finance-pie-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <slot name="tools"></slot>
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

// 接收的属性
const props = defineProps({
  // 图表标题
  title: {
    type: String,
    default: '收支比例'
  },
  // 饼图数据 - 格式为 [{name: '类别1', value: 100}, {name: '类别2', value: 200}]
  chartData: {
    type: Array,
    default: () => []
  },
  // 是否显示内环
  donut: {
    type: Boolean,
    default: true
  },
  // 是否允许图例点击切换数据可见性
  legendSelectable: {
    type: Boolean,
    default: true
  },
  // 自定义颜色方案
  colorScheme: {
    type: Array,
    default: () => [
      '#52c41a', // 绿色 - 收入
      '#ff4d4f', // 红色 - 支出
      '#1890ff', // 蓝色
      '#faad14', // 黄色
      '#722ed1', // 紫色
      '#13c2c2', // 青色
      '#eb2f96', // 粉色
      '#fa8c16'  // 橙色
    ]
  },
  // 是否显示图表工具箱
  showTools: {
    type: Boolean,
    default: true
  },
  // 是否正在加载数据
  loading: {
    type: Boolean,
    default: false
  },
  // 空数据提示文本
  emptyText: {
    type: String,
    default: '暂无数据'
  }
});

// 计算属性：检查图表数据是否为空
const isEmpty = computed(() => {
  // 更严格的空数据检测
  if (!props.chartData || props.chartData.length === 0) return true;
  
  // 检查是否所有值都为0或非有效数字
  return props.chartData.every(item => {
    const value = Number(item.value);
    return isNaN(value) || value === 0;
  });
});

// 状态变量
const chartContainer = ref(null);
const chartInstance = ref(null);

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return;
  
  // 销毁旧实例
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  
  // 初始化ECharts实例
  chartInstance.value = echarts.init(chartContainer.value);
  console.log('饼图实例已创建');
  
  // 首次渲染图表
  updateChart();
};

// 更新图表数据
const updateChart = () => {
  if (!chartInstance.value) return;
  
  console.log('更新饼图数据:', props.chartData);
  
  // 设置饼图配置
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 10,
      type: 'scroll',
      selectedMode: props.legendSelectable ? 'multiple' : false,
      formatter: function(name) {
        // 查找图例对应的数据项
        const data = props.chartData.find(item => item.name === name);
        if (!data) return name;
        
        // 格式化金额并显示在图例中
        const formattedValue = new Intl.NumberFormat('zh-CN', {
          style: 'currency',
          currency: 'CNY'
        }).format(data.value);
        
        // 根据图例名称长度决定是否需要缩略
        if (name.length > 6) {
          return `${name.substring(0, 6)}... (${formattedValue})`;
        }
        return `${name} (${formattedValue})`;
      }
    },
    toolbox: props.showTools ? {
      feature: {
        saveAsImage: {
          title: '保存为图片',
          name: '收支比例图'
        }
      }
    } : undefined,
    series: [
      {
        name: props.title,
        type: 'pie',
        radius: props.donut ? ['40%', '70%'] : '70%',
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: true
        },
        data: isEmpty.value ? [] : props.chartData
      }
    ],
    color: props.colorScheme
  };
  
  // 如果没有数据，添加一个空状态提示
  if (isEmpty.value) {
    option.title = {
      text: props.emptyText,
      left: 'center',
      top: 'center',
      textStyle: {
        color: '#999',
        fontSize: 16,
        fontWeight: 'normal'
      }
    };
  } else {
    option.title = null;
  }
  
  // 更新图表
  chartInstance.value.setOption(option, true);
};

// 监听数据变化，更新图表
watch(
  () => props.chartData,
  (newValue) => {
    console.log('饼图数据已变化:', newValue);
    if (chartInstance.value) {
      updateChart();
    }
  },
  { deep: true }
);

// 监听loading状态变化
watch(
  () => props.loading,
  (newValue) => {
    if (!chartInstance.value) return;
    
    if (newValue) {
      // 显示加载状态
      chartInstance.value.showLoading({
        text: '加载中...',
        maskColor: 'rgba(255, 255, 255, 0.8)'
      });
    } else {
      // 隐藏加载状态
      chartInstance.value.hideLoading();
    }
  }
);

// 处理窗口大小变化
const handleResize = () => {
  chartInstance.value?.resize();
};

// 组件挂载后初始化图表
onMounted(() => {
  console.log('饼图组件已挂载');
  setTimeout(() => {
    initChart();
  }, 0);
  window.addEventListener('resize', handleResize);
});

// 组件卸载前清理
onUnmounted(() => {
  console.log('饼图组件将卸载');
  if (chartInstance.value) {
    chartInstance.value.dispose();
    chartInstance.value = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.finance-pie-chart {
  width: 100%;
  height: 100%;
  position: relative;
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
