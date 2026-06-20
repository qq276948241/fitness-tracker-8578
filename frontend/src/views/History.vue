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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
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

const activeTab = ref('workout')
const dateRange = ref([])
const weightDateRange = ref([])
const filterType = ref('')
const workouts = ref([])
const weightRecords = ref([])
const loading = ref(false)
const weightLoading = ref(false)
const submitting = ref(false)

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
