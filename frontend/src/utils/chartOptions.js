import * as echarts from 'echarts'

export function getWeeklyWorkoutOption(weeklyData = []) {
  const days = weeklyData.map(item => item.date.slice(5))
  const durations = weeklyData.map(item => item.duration)
  const calories = weeklyData.map(item => item.calories)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
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
      data: days,
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#909399', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '分钟',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', fontSize: 12 }
    },
    series: [{
      type: 'bar',
      data: durations,
      barWidth: '40%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      }
    }]
  }
}

export function getWeightTrendOption(weightHistory = []) {
  const dates = weightHistory.map(item => item.date.slice(5))
  const weights = weightHistory.map(item => item.weight)

  return {
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
    series: [{
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
      itemStyle: { color: '#667eea' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
        ])
      }
    }]
  }
}

export function getWorkoutTypePieOption(workoutTypes = {}) {
  const data = Object.entries(workoutTypes).map(([name, value]) => ({ name, value }))

  return {
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
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: data.length > 0 ? data : [{ name: '暂无数据', value: 0 }],
      color: ['#667eea', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#409eff']
    }]
  }
}

export function getWeeklyStatsOption(weeklyData = []) {
  const days = weeklyData.map(item => item.date.slice(5))
  const durations = weeklyData.map(item => item.duration)
  const calories = weeklyData.map(item => item.calories)

  return {
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
}
