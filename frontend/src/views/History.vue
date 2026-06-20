<template>
  <div class="history-page">
    <h2 class="page-title">历史记录</h2>

    <el-tabs v-model="activeTab" class="history-tabs">
      <el-tab-pane label="训练记录" name="workout">
        <div class="card">
          <div class="filter-bar">
            <el-radio-group v-model="viewMode" class="view-switch">
              <el-radio-button value="list"><el-icon><List /></el-icon> 列表</el-radio-button>
              <el-radio-button value="calendar"><el-icon><Calendar /></el-icon> 日历</el-radio-button>
            </el-radio-group>
            <template v-if="viewMode === 'list'">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
              <el-select v-model="filterType" placeholder="训练类型" clearable style="width: 150px">
                <el-option label="力量训练" value="力量训练" />
                <el-option label="有氧训练" value="有氧训练" />
                <el-option label="HIIT" value="HIIT" />
                <el-option label="瑜伽" value="瑜伽" />
                <el-option label="跑步" value="跑步" />
                <el-option label="游泳" value="游泳" />
                <el-option label="骑行" value="骑行" />
                <el-option label="其他" value="其他" />
              </el-select>
              <el-button type="primary" :icon="Search" @click="loadWorkouts">查询</el-button>
              <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
            </template>
          </div>

          <div v-if="viewMode === 'list'">
            <el-table :data="workouts" style="width: 100%" v-loading="loading">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="workout_type" label="训练类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="getWorkoutTypeColor(row.workout_type)" size="small">
                    {{ row.workout_type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="duration" label="时长(分钟)" width="100" />
              <el-table-column prop="calories" label="消耗(千卡)" width="100" />
              <el-table-column prop="notes" label="备注" show-overflow-tooltip />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="editWorkout(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="deleteWorkoutItem(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-pagination
              v-if="workouts.length > 0"
              class="pagination"
              layout="total, prev, pager, next"
              :total="workouts.length"
              :page-size="10"
              background
            />
          </div>

          <div v-else class="calendar-view" v-loading="calendarLoading">
            <div class="calendar-header">
              <el-button :icon="ArrowLeft" circle @click="prevMonth" />
              <span class="calendar-title">{{ calendarYear }}年{{ calendarMonth }}月</span>
              <el-button :icon="ArrowRight" circle @click="nextMonth" />
              <el-button type="primary" plain size="small" @click="goToday" style="margin-left: 12px">今天</el-button>
              <div class="calendar-summary">
                <el-tag type="success">打卡 {{ calendarSummary.checked_days }}/{{ calendarSummary.total_days }} 天</el-tag>
                <el-tag type="warning">训练 {{ calendarSummary.total_duration }} 分钟</el-tag>
                <el-tag type="danger">消耗 {{ calendarSummary.total_calories }} 千卡</el-tag>
              </div>
            </div>

            <div class="calendar-grid">
              <div class="calendar-weekday" v-for="w in weekdays" :key="w">{{ w }}</div>
              <div
                v-for="cell in calendarCells"
                :key="cell.key"
                class="calendar-cell"
                :class="{
                  'other-month': !cell.currentMonth,
                  'checked': cell.checked_in,
                  'today': cell.isToday
                }"
                @click="cell.currentMonth && selectDay(cell)"
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
        </div>
      </el-tab-pane>

      <el-tab-pane label="体重记录" name="weight">
        <div class="card">
          <div class="filter-bar">
            <el-date-picker
              v-model="weightDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
            <el-button type="primary" :icon="Search" @click="loadWeights">查询</el-button>
            <el-button :icon="Refresh" @click="resetWeightFilters">重置</el-button>
          </div>

          <el-table :data="weightRecords" style="width: 100%" v-loading="weightLoading">
            <el-table-column prop="date" label="日期" width="150" />
            <el-table-column prop="weight" label="体重(kg)" width="120">
              <template #default="{ row }">
                <span class="weight-value">{{ row.weight.toFixed(1) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="body_fat" label="体脂率(%)" width="120">
              <template #default="{ row }">
                {{ row.body_fat ? row.body_fat.toFixed(1) : '--' }}
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="editWeight(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="deleteWeightItem(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="weightRecords.length > 0"
            class="pagination"
            layout="total, prev, pager, next"
            :total="weightRecords.length"
            :page-size="10"
            background
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="workoutDialogVisible" title="编辑训练记录" width="500px">
      <el-form :model="workoutForm" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker
            v-model="workoutForm.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="训练类型">
          <el-select v-model="workoutForm.workout_type" placeholder="请选择训练类型" style="width: 100%">
            <el-option label="力量训练" value="力量训练" />
            <el-option label="有氧训练" value="有氧训练" />
            <el-option label="HIIT" value="HIIT" />
            <el-option label="瑜伽" value="瑜伽" />
            <el-option label="游泳" value="游泳" />
            <el-option label="跑步" value="跑步" />
            <el-option label="骑行" value="骑行" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长">
          <el-input-number v-model="workoutForm.duration" :min="0" :max="600" style="width: 100%" />
          <span style="margin-left: 10px; color: #909399">分钟</span>
        </el-form-item>
        <el-form-item label="消耗">
          <el-input-number v-model="workoutForm.calories" :min="0" :max="10000" style="width: 100%" />
          <span style="margin-left: 10px; color: #909399">千卡</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="workoutForm.notes"
            type="textarea"
            :rows="3"
            placeholder="记录一下训练感受..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workoutDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitWorkoutEdit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="weightDialogVisible" title="编辑体重记录" width="400px">
      <el-form :model="weightForm" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker
            v-model="weightForm.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="体重">
          <el-input-number v-model="weightForm.weight" :min="20" :max="300" :step="0.1" style="width: 100%" />
          <span style="margin-left: 10px; color: #909399">kg</span>
        </el-form-item>
        <el-form-item label="体脂率">
          <el-input-number v-model="weightForm.body_fat" :min="5" :max="50" :step="0.1" style="width: 100%" />
          <span style="margin-left: 10px; color: #909399">%</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="weightForm.notes"
            type="textarea"
            :rows="2"
            placeholder="备注..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="weightDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitWeightEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, List, Calendar, ArrowLeft, ArrowRight,
  CircleCheckFilled, Clock, Star, DataLine
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import {
  getWorkouts,
  updateWorkout,
  deleteWorkout
} from '@/api/workout'
import {
  getWeightRecords,
  updateWeightRecord,
  deleteWeightRecord
} from '@/api/weight'
import { getCalendarData } from '@/api/stats'

const activeTab = ref('workout')
const viewMode = ref('list')
const dateRange = ref([])
const weightDateRange = ref([])
const filterType = ref('')
const workouts = ref([])
const weightRecords = ref([])
const loading = ref(false)
const weightLoading = ref(false)
const submitting = ref(false)

const calendarLoading = ref(false)
const calendarYear = ref(dayjs().year())
const calendarMonth = ref(dayjs().month() + 1)
const calendarDays = ref([])
const calendarSummary = ref({ checked_days: 0, total_days: 0, total_duration: 0, total_calories: 0 })
const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const workoutDialogVisible = ref(false)
const weightDialogVisible = ref(false)
const editingWorkoutId = ref(null)
const editingWeightId = ref(null)

const workoutForm = ref({
  date: '',
  workout_type: '',
  duration: 30,
  calories: null,
  notes: ''
})

const weightForm = ref({
  date: '',
  weight: 60,
  body_fat: null,
  notes: ''
})

const calendarCells = computed(() => {
  const firstDay = dayjs(`${calendarYear.value}-${String(calendarMonth.value).padStart(2, '0')}-01`)
  const startWeekday = firstDay.day()
  const cells = []

  for (let i = startWeekday; i > 0; i--) {
    const d = firstDay.subtract(i, 'day')
    cells.push({
      key: `prev-${d.format('YYYY-MM-DD')}`,
      currentMonth: false,
      day: d.date()
    })
  }

  for (const day of calendarDays.value) {
    const today = dayjs().format('YYYY-MM-DD')
    cells.push({
      key: `cur-${day.date}`,
      currentMonth: true,
      day: day.day,
      date: day.date,
      checked_in: day.checked_in,
      workout_count: day.workout_count,
      duration: day.duration,
      calories: day.calories,
      types: day.types || [],
      weight: day.weight,
      isToday: day.date === today
    })
  }

  while (cells.length % 7 !== 0) {
    const lastDate = cells[cells.length - 1]
    const nextDate = dayjs(lastDate.date || `${calendarYear.value}-${String(calendarMonth.value).padStart(2, '0')}-01`).add(1, 'month').startOf('month')
    const offset = cells.length - startWeekday - calendarDays.value.length
    const d = nextDate.add(offset, 'day')
    cells.push({
      key: `next-${d.format('YYYY-MM-DD')}`,
      currentMonth: false,
      day: d.date()
    })
  }

  return cells
})

const getWorkoutTypeColor = (type) => {
  const colors = {
    '力量训练': '',
    '有氧训练': 'success',
    'HIIT': 'warning',
    '瑜伽': 'info',
    '跑步': 'success',
    '游泳': 'primary',
    '骑行': '',
    '其他': 'info'
  }
  return colors[type] || ''
}

const loadWorkouts = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (filterType.value) {
      params.workout_type = filterType.value
    }
    const res = await getWorkouts(params)
    workouts.value = res
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const loadCalendar = async () => {
  calendarLoading.value = true
  try {
    const res = await getCalendarData(calendarYear.value, calendarMonth.value)
    calendarDays.value = res.days
    calendarSummary.value = res.summary
  } catch (err) {
    console.error(err)
  } finally {
    calendarLoading.value = false
  }
}

const prevMonth = () => {
  if (calendarMonth.value === 1) {
    calendarMonth.value = 12
    calendarYear.value--
  } else {
    calendarMonth.value--
  }
  loadCalendar()
}

const nextMonth = () => {
  if (calendarMonth.value === 12) {
    calendarMonth.value = 1
    calendarYear.value++
  } else {
    calendarMonth.value++
  }
  loadCalendar()
}

const goToday = () => {
  const now = dayjs()
  calendarYear.value = now.year()
  calendarMonth.value = now.month() + 1
  loadCalendar()
}

const selectDay = (cell) => {
  if (cell.checked_in) {
    ElMessage.success(`${cell.date} 打卡成功！训练 ${cell.workout_count} 次`)
  } else {
    ElMessage.info(`${cell.date} 还没有打卡记录`)
  }
}

watch(viewMode, (val) => {
  if (val === 'calendar' && calendarDays.value.length === 0) {
    loadCalendar()
  }
})

const loadWeights = async () => {
  weightLoading.value = true
  try {
    const params = {}
    if (weightDateRange.value && weightDateRange.value.length === 2) {
      params.start_date = weightDateRange.value[0]
      params.end_date = weightDateRange.value[1]
    }
    const res = await getWeightRecords(params)
    weightRecords.value = res
  } catch (err) {
    console.error(err)
  } finally {
    weightLoading.value = false
  }
}

const resetFilters = () => {
  dateRange.value = []
  filterType.value = ''
  loadWorkouts()
}

const resetWeightFilters = () => {
  weightDateRange.value = []
  loadWeights()
}

const editWorkout = (row) => {
  editingWorkoutId.value = row.id
  workoutForm.value = {
    date: row.date,
    workout_type: row.workout_type,
    duration: row.duration,
    calories: row.calories,
    notes: row.notes
  }
  workoutDialogVisible.value = true
}

const editWeight = (row) => {
  editingWeightId.value = row.id
  weightForm.value = {
    date: row.date,
    weight: row.weight,
    body_fat: row.body_fat,
    notes: row.notes
  }
  weightDialogVisible.value = true
}

const submitWorkoutEdit = async () => {
  try {
    submitting.value = true
    await updateWorkout(editingWorkoutId.value, workoutForm.value)
    ElMessage.success('更新成功')
    workoutDialogVisible.value = false
    loadWorkouts()
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const submitWeightEdit = async () => {
  try {
    submitting.value = true
    await updateWeightRecord(editingWeightId.value, weightForm.value)
    ElMessage.success('更新成功')
    weightDialogVisible.value = false
    loadWeights()
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const deleteWorkoutItem = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条训练记录吗？', '确认删除', {
      type: 'warning'
    })
    await deleteWorkout(id)
    ElMessage.success('删除成功')
    loadWorkouts()
    if (viewMode.value === 'calendar') {
      loadCalendar()
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error(err)
    }
  }
}

const deleteWeightItem = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条体重记录吗？', '确认删除', {
      type: 'warning'
    })
    await deleteWeightRecord(id)
    ElMessage.success('删除成功')
    loadWeights()
  } catch (err) {
    if (err !== 'cancel') {
      console.error(err)
    }
  }
}

onMounted(() => {
  loadWorkouts()
  loadWeights()
})
</script>

<style scoped>
.history-tabs {
  background: #fff;
  border-radius: 12px;
  padding: 0 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.view-switch {
  margin-right: auto;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
  display: flex;
}

.weight-value {
  font-weight: 600;
  color: #67c23a;
}

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
