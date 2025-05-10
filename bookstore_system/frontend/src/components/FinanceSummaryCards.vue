<template>
  <div class="summary-cards">
    <div class="card income">
      <div class="card-content">
        <div class="card-icon">
          <i class="fas fa-chart-line"></i>
        </div>
        <div class="card-data">
          <h3>总收入</h3>
          <div class="amount">¥{{ formatAmount(income) }}</div>
          <div v-if="compareData.income_change_rate" class="change-rate" 
               :class="compareData.income_change_rate >= 0 ? 'positive' : 'negative'">
            <i :class="compareData.income_change_rate >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ Math.abs(compareData.income_change_rate) }}%
          </div>
        </div>
      </div>
    </div>
    
    <div class="card expense">
      <div class="card-content">
        <div class="card-icon">
          <i class="fas fa-money-bill-wave"></i>
        </div>
        <div class="card-data">
          <h3>总支出</h3>
          <div class="amount">¥{{ formatAmount(expense) }}</div>
          <div v-if="compareData.expense_change_rate" class="change-rate" 
               :class="compareData.expense_change_rate >= 0 ? 'negative' : 'positive'">
            <i :class="compareData.expense_change_rate >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ Math.abs(compareData.expense_change_rate) }}%
          </div>
        </div>
      </div>
    </div>
    
    <div class="card profit">
      <div class="card-content">
        <div class="card-icon">
          <i class="fas fa-wallet"></i>
        </div>
        <div class="card-data">
          <h3>净利润</h3>
          <div class="amount">¥{{ formatAmount(profit) }}</div>
          <div v-if="compareData.profit_change_rate" class="change-rate" 
               :class="compareData.profit_change_rate >= 0 ? 'positive' : 'negative'">
            <i :class="compareData.profit_change_rate >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ Math.abs(compareData.profit_change_rate) }}%
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

// 接收的属性
const props = defineProps({
  income: {
    type: Number,
    default: 0
  },
  expense: {
    type: Number,
    default: 0
  },
  profit: {
    type: Number,
    default: 0
  },
  compareData: {
    type: Object,
    default: () => ({
      income_change_rate: 0,
      expense_change_rate: 0,
      profit_change_rate: 0
    })
  }
});

// 格式化金额
const formatAmount = (amount) => {
  return parseFloat(amount || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};
</script>

<style scoped>
.summary-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  flex: 1;
  min-width: 250px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-content {
  display: flex;
  padding: 20px;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-right: 15px;
  font-size: 24px;
}

.income .card-icon {
  background-color: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.expense .card-icon {
  background-color: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.profit .card-icon {
  background-color: rgba(24, 144, 255, 0.2);
  color: #1890FF;
}

.card-data {
  flex: 1;
}

h3 {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.amount {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.income .amount {
  color: #4CAF50;
}

.expense .amount {
  color: #F44336;
}

.profit .amount {
  color: #1890FF;
}

.change-rate {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.positive {
  color: #4CAF50;
}

.negative {
  color: #F44336;
}

@media (max-width: 768px) {
  .card {
    flex: 100%;
  }
}
</style>
