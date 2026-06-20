<template>
  <div class="stats-page">
    <h2 class="page-title">数据统计</h2>

    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_workouts || 0 }}</div>
          <div class="stat-label">累计训练次数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card green">
          <div class="stat-value">{{ stats.total_duration || 0 }}</div>
          <div class="stat-label">累计训练分钟</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card orange">
          <div class="stat-value">{{ stats.total_calories || 0 }}</div>
          <div class="stat-label">消耗卡路里</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card blue">
          <div class="stat-value">{{ avgDuration }}</div>
          <div class="stat-label">平均每次(分钟)</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card">
          <h3 class="chart-title">训练类型分布</h3>
          <BaseChart :option="typePieOption" height="280px" />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <h3 class="chart-title">体重变化趋势</h3>
          <BaseChart :option="weightTrendOption" height="280px" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <div class="card">
          <h3 class="chart-title">近7天训练时长</h3>
          <BaseChart :option="weeklyStatsOption" height="320px" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStatsStore } from '@/stores/stats'
import BaseChart from '@/components/BaseChart.vue'
import {
  getWorkoutTypePieOption,
  getWeightTrendOption,
  getWeeklyStatsOption
} from '@/utils/chartOptions'

const statsStore = useStatsStore()

const stats = computed(() => statsStore.stats)

const avgDuration = computed(() => {
  if (!stats.value.total_workouts) return 0
  return Math.round(stats.value.total_duration / stats.value.total_workouts)
})

const typePieOption = computed(() => {
  return getWorkoutTypePieOption(stats.value.workout_types || {})
})

const weightTrendOption = computed(() => {
  return getWeightTrendOption(stats.value.weight_history || [])
})

const weeklyStatsOption = computed(() => {
  return getWeeklyStatsOption(stats.value.weekly_data || [])
})

onMounted(() => {
  statsStore.loadStats()
})
</script>

<style scoped>
.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}
</style>
