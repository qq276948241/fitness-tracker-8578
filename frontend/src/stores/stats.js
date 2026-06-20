import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getStats, getCalendarData } from '@/api/stats'
import dayjs from 'dayjs'

export const useStatsStore = defineStore('stats', () => {
  const stats = ref({})
  const calendarMap = ref({})
  const loading = ref(false)

  const hasStats = computed(() => Object.keys(stats.value).length > 0)

  const loadStats = async (force = false) => {
    if (hasStats.value && !force) return stats.value
    loading.value = true
    try {
      const data = await getStats()
      stats.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const refreshStats = () => {
    return loadStats(true)
  }

  const getCalendarKey = (year, month) => `${year}-${String(month).padStart(2, '0')}`

  const loadCalendarData = async (year, month, force = false) => {
    const key = getCalendarKey(year, month)
    if (calendarMap.value[key] && !force) {
      return calendarMap.value[key]
    }
    const data = await getCalendarData(year, month)
    calendarMap.value[key] = data
    return data
  }

  const refreshCalendar = (year, month) => {
    return loadCalendarData(year, month, true)
  }

  const targetAchieved = computed(() => {
    return stats.value.target_weight &&
           stats.value.current_weight &&
           stats.value.current_weight <= stats.value.target_weight
  })

  const targetPercentage = computed(() => {
    if (!stats.value.target_weight || !stats.value.current_weight) return 0
    const current = stats.value.current_weight
    const target = stats.value.target_weight
    const initial = stats.value.weight_history?.[0]?.weight || current
    const total = Math.abs(initial - target)
    if (total === 0) return 100
    const done = Math.abs(initial - current)
    let pct = (done / total) * 100
    return Math.min(100, Math.max(0, Math.round(pct)))
  })

  const targetColor = computed(() => {
    if (targetAchieved.value) return '#67c23a'
    if (targetPercentage.value >= 70) return '#95d475'
    if (targetPercentage.value >= 40) return '#e6a23c'
    return '#f56c6c'
  })

  const $reset = () => {
    stats.value = {}
    calendarMap.value = {}
    loading.value = false
  }

  return {
    stats,
    calendarMap,
    loading,
    hasStats,
    targetAchieved,
    targetPercentage,
    targetColor,
    loadStats,
    refreshStats,
    loadCalendarData,
    refreshCalendar,
    $reset
  }
})
