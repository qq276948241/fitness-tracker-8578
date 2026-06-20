<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: {
    type: Object,
    required: true
  },
  height: {
    type: [String, Number],
    default: '300px'
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(props.option)
}

const resizeHandler = () => {
  chartInstance?.resize()
}

watch(() => props.option, (newOption) => {
  if (chartInstance) {
    chartInstance.setOption(newOption, true)
    chartInstance.resize()
  }
}, { deep: true })

onMounted(async () => {
  await nextTick()
  initChart()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
  chartInstance?.dispose()
  chartInstance = null
})

defineExpose({
  resize: resizeHandler
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: v-bind(height);
}
</style>
