<template>
  <div class="calendar-view" v-loading="loading">
    <div class="calendar-header">
      <el-button :icon="ArrowLeft" circle @click="prevMonth" />
      <span class="calendar-title">{{ year }}年{{ month }}月</span>
      <el-button :icon="ArrowRight" circle @click="nextMonth" />
      <el-button type="primary" plain size="small" @click="goToday" style="margin-left: 12px">今天</el-button>
      <div class="calendar-summary">
        <el-tag type="success">打卡 {{ summary.checked_days }}/{{ summary.total_days }} 天</el-tag>
        <el-tag type="warning">训练 {{ summary.total_duration }} 分钟</el-tag>
        <el-tag type="danger">消耗 {{ summary.total_calories }} 千卡</el-tag>
      </div>
    </div>

    <div class="calendar-grid">
      <div class="calendar-weekday" v-for="w in weekdays" :key="w">{{ w }}</div>
      <div
        v-for="cell in cells"
        :key="cell.key"
        class="calendar-cell"
        :class="{
          'other-month': !cell.currentMonth,
          'checked': cell.checked_in,
          'today': cell.isToday
        }"
        @click="cell.currentMonth && handleDayClick(cell)"
      >
        <template v-if="cell.currentMonth">
          <div class="cell-header">
            <span class="cell-day">{{ cell.day }}</span>
            <el-icon v-if="cell.checked_in" class="cell-check"><CircleCheckFilled /></el-icon>
          </div>
          <div v-if="cell.checked_in" class="cell-body">
            <div class="cell-types">
              <el-tag
                v-for="t in cell.types.slice(0, 2)"
                :key="t"
                :type="getWorkoutTypeColor(t)"
                size="small"
              >
                {{ t }}
              </el-tag>
              <span v-if="cell.types.length > 2" class="cell-more">+{{ cell.types.length - 2 }}</span>
            </div>
            <div class="cell-meta">
              <span v-if="cell.duration"><el-icon><Clock /></el-icon>{{ cell.duration }}min</span>
              <span v-if="cell.calories"><el-icon><Star /></el-icon>{{ cell.calories }}kcal</span>
            </div>
          </div>
          <div v-if="cell.weight" class="cell-weight">
            <el-icon><DataLine /></el-icon>{{ cell.weight.toFixed(1) }}kg
          </div>
        </template>
      </div>
    </div>

    <div class="calendar-legend">
      <span class="legend-item"><span class="legend-box checked"></span>已打卡</span>
      <span class="legend-item"><span class="legend-box"></span>未打卡</span>
      <span class="legend-item"><span class="legend-box today"></span>今天</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ArrowLeft, ArrowRight, CircleCheckFilled, Clock, Star, DataLine } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getWorkoutTypeColor } from '@/utils/constants'

const props = defineProps({
  year: {
    type: Number,
    default: () => dayjs().year()
  },
  month: {
    type: Number,
    default: () => dayjs().month() + 1
  },
  days: {
    type: Array,
    default: () => []
  },
  summary: {
    type: Object,
    default: () => ({ checked_days: 0, total_days: 0, total_duration: 0, total_calories: 0 })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:year', 'update:month', 'change', 'day-click'])

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const innerYear = ref(props.year)
const innerMonth = ref(props.month)

watch(() => props.year, (val) => { innerYear.value = val })
watch(() => props.month, (val) => { innerMonth.value = val })

const cells = computed(() => {
  const firstDay = dayjs(`${innerYear.value}-${String(innerMonth.value).padStart(2, '0')}-01`)
  const startWeekday = firstDay.day()
  const dayMap = {}
  for (const d of props.days) {
    dayMap[d.date] = d
  }

  const cellsList = []
  const todayStr = dayjs().format('YYYY-MM-DD')

  const daysInMonth = firstDay.daysInMonth()

  for (let i = startWeekday; i > 0; i--) {
    const d = firstDay.subtract(i, 'day')
    cellsList.push({
      key: `prev-${d.format('YYYY-MM-DD')}`,
      currentMonth: false,
      day: d.date()
    })
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${innerYear.value}-${String(innerMonth.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const dayData = dayMap[dateStr] || {}
    cellsList.push({
      key: `cur-${dateStr}`,
      currentMonth: true,
      day,
      date: dateStr,
      checked_in: !!dayData.checked_in,
      workout_count: dayData.workout_count || 0,
      duration: dayData.duration || 0,
      calories: dayData.calories || 0,
      types: dayData.types || [],
      weight: dayData.weight,
      isToday: dateStr === todayStr
    })
  }

  while (cellsList.length % 7 !== 0) {
    const lastIdx = cellsList.length - 1
    const lastDateStr = cellsList[lastIdx].date || `${innerYear.value}-${String(innerMonth.value).padStart(2, '0')}-01`
    const nextDate = dayjs(lastDateStr).add(1, 'day')
    cellsList.push({
      key: `next-${nextDate.format('YYYY-MM-DD')}`,
      currentMonth: false,
      day: nextDate.date()
    })
  }

  return cellsList
})

const prevMonth = () => {
  if (innerMonth.value === 1) {
    innerMonth.value = 12
    innerYear.value--
  } else {
    innerMonth.value--
  }
  emitChange()
}

const nextMonth = () => {
  if (innerMonth.value === 12) {
    innerMonth.value = 1
    innerYear.value++
  } else {
    innerMonth.value++
  }
  emitChange()
}

const goToday = () => {
  const now = dayjs()
  innerYear.value = now.year()
  innerMonth.value = now.month() + 1
  emitChange()
}

const emitChange = () => {
  emit('update:year', innerYear.value)
  emit('update:month', innerMonth.value)
  emit('change', { year: innerYear.value, month: innerMonth.value })
}

const handleDayClick = (cell) => {
  emit('day-click', cell)
}
</script>

<style scoped>
.calendar-view {
  min-height: 400px;
}

.calendar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.calendar-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  min-width: 120px;
  text-align: center;
}

.calendar-summary {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-weekday {
  text-align: center;
  font-weight: 600;
  color: #909399;
  padding: 8px 0;
  font-size: 13px;
}

.calendar-cell {
  min-height: 90px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.calendar-cell:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.calendar-cell.other-month {
  background: #fafafa;
  opacity: 0.5;
  cursor: default;
}

.calendar-cell.checked {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-color: #b3e19d;
}

.calendar-cell.today {
  border: 2px solid #409eff;
}

.cell-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.cell-day {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.cell-check {
  color: #67c23a;
  font-size: 16px;
}

.cell-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cell-types {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  align-items: center;
}

.cell-more {
  font-size: 11px;
  color: #909399;
}

.cell-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #606266;
  flex-wrap: wrap;
}

.cell-meta span {
  display: flex;
  align-items: center;
  gap: 2px;
}

.cell-weight {
  margin-top: 4px;
  font-size: 11px;
  color: #e6a23c;
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: 600;
}

.calendar-legend {
  display: flex;
  gap: 20px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.legend-box {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background: #fff;
}

.legend-box.checked {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-color: #b3e19d;
}

.legend-box.today {
  border: 2px solid #409eff;
}
</style>
