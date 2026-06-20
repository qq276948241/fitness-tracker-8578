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
          <div ref="typeChartRef" class="chart"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <h3 class="chart-title">体重变化趋势</h3>
          <div ref="weightChartRef" class="chart"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <div class="card">
          <h3 class="chart-title">近7天训练时长</h3>
          <div ref="weeklyChartRef" class="chart-horizontal"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { getStats } from '@/api/stats'

const stats = ref({})
const typeChartRef = ref(null)
const weightChartRef = ref(null)
const weeklyChartRef = ref(null)

let typeChart = null
let weightChart = null
let weeklyChart = null

const avgDuration = computed(() => {
  if (!stats.value.total_workouts) return 0
  return Math.round(stats.value.total_duration / stats.value.total_workouts)
})

const loadStats = async () => {
  try {
    const res = await getStats()
    stats.value = res
    await nextTick()
    renderCharts()
  } catch (err) {
    console.error(err)
  }
}

const renderCharts = () => {
  renderTypeChart()
  renderWeightChart()
  renderWeeklyChart()
}

const renderTypeChart = () => {
  if (!typeChartRef.value) return

  if (!typeChart) {
    typeChart = echarts.init(typeChartRef.value)
  }

  const data = Object.entries(stats.value.workout_types || {}).map(([name, value]) => ({
    name,
    value
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}次 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#606266', fontSize: 13 }
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: data.length > 0 ? data : [{ name: '暂无数据', value: 0 }],
        color: ['#667eea', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#409eff']
      }
    ]
  }

  typeChart.setOption(option)
}

const renderWeightChart = () => {
  if (!weightChartRef.value) return

  if (!weightChart) {
    weightChart = echarts.init(weightChartRef.value)
  }

  const history = stats.value.weight_history || []
  const dates = history.map(item => item.date.slice(5))
  const weights = history.map(item => item.weight)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>体重: {c} kg'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#909399', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', fontSize: 12 }
    },
    series: [
      {
        data: weights,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        },
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        }
      }
    ]
  }

  weightChart.setOption(option)
}

const renderWeeklyChart = () => {
  if (!weeklyChartRef.value) return

  if (!weeklyChart) {
    weeklyChart = echarts.init(weeklyChartRef.value)
  }

  const weeklyData = stats.value.weekly_data || []
  const days = weeklyData.map(item => item.date.slice(5))
  const durations = weeklyData.map(item => item.duration)
  const calories = weeklyData.map(item => item.calories)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['训练时长', '消耗卡路里'],
      top: 0,
      textStyle: { color: '#606266' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: days,
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#909399', fontSize: 12 }
    },
    yAxis: [
      {
        type: 'value',
        name: '分钟',
        position: 'left',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: '#f0f2f5' } },
        axisLabel: { color: '#909399', fontSize: 12 }
      },
      {
        type: 'value',
        name: '千卡',
        position: 'right',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { color: '#909399', fontSize: 12 }
      }
    ],
    series: [
      {
        name: '训练时长',
        type: 'bar',
        data: durations,
        barWidth: '30%',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ])
        }
      },
      {
        name: '消耗卡路里',
        type: 'line',
        yAxisIndex: 1,
        data: calories,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#e6a23c' },
        itemStyle: { color: '#e6a23c' }
      }
    ]
  }

  weeklyChart.setOption(option)
}

onMounted(() => {
  loadStats()

  window.addEventListener('resize', () => {
    typeChart?.resize()
    weightChart?.resize()
    weeklyChart?.resize()
  })
})
</script>

<style scoped>
.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.chart {
  height: 280px;
  width: 100%;
}

.chart-horizontal {
  height: 320px;
  width: 100%;
}
</style>
