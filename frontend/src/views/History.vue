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
                <el-option
                  v-for="t in workoutTypes"
                  :key="t"
                  :label="t"
                  :value="t"
                />
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

          <CalendarView
            v-else
            v-model:year="calendarYear"
            v-model:month="calendarMonth"
            :days="calendarDays"
            :summary="calendarSummary"
            :loading="calendarLoading"
            @change="handleCalendarChange"
            @day-click="handleDayClick"
          />
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
            <el-option
              v-for="t in workoutTypes"
              :key="t"
              :label="t"
              :value="t"
            />
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
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, List, Calendar } from '@element-plus/icons-vue'
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
import { useStatsStore } from '@/stores/stats'
import { WORKOUT_TYPES, getWorkoutTypeColor } from '@/utils/constants'
import CalendarView from '@/components/CalendarView.vue'

const statsStore = useStatsStore()

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
const workoutTypes = WORKOUT_TYPES

const calendarLoading = ref(false)
const calendarYear = ref(dayjs().year())
const calendarMonth = ref(dayjs().month() + 1)
const calendarDays = ref([])
const calendarSummary = ref({ checked_days: 0, total_days: 0, total_duration: 0, total_calories: 0 })

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
    const data = await statsStore.loadCalendarData(calendarYear.value, calendarMonth.value)
    calendarDays.value = data.days
    calendarSummary.value = data.summary
  } catch (err) {
    console.error(err)
  } finally {
    calendarLoading.value = false
  }
}

const handleCalendarChange = ({ year, month }) => {
  calendarYear.value = year
  calendarMonth.value = month
  loadCalendar()
}

const handleDayClick = (cell) => {
  if (cell.checked_in) {
    ElMessage.success(`${cell.date} 打卡成功！训练 ${cell.workout_count} 次`)
  } else {
    ElMessage.info(`${cell.date} 还没有打卡记录`)
  }
}

watch(viewMode, (val) => {
  if (val === 'calendar') {
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
    await Promise.all([
      loadWorkouts(),
      statsStore.refreshStats(),
      statsStore.refreshCalendar(calendarYear.value, calendarMonth.value)
    ])
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
    await Promise.all([
      loadWeights(),
      statsStore.refreshStats(),
      statsStore.refreshCalendar(calendarYear.value, calendarMonth.value)
    ])
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
    await Promise.all([
      loadWorkouts(),
      statsStore.refreshStats(),
      statsStore.refreshCalendar(calendarYear.value, calendarMonth.value)
    ])
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
    await Promise.all([
      loadWeights(),
      statsStore.refreshStats(),
      statsStore.refreshCalendar(calendarYear.value, calendarMonth.value)
    ])
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
</style>
