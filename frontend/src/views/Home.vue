<template>
  <div class="home-page">
    <h2 class="page-title">今日打卡</h2>

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
          <div class="stat-value">{{ stats.current_weight ? stats.current_weight.toFixed(1) : '--' }}</div>
          <div class="stat-label">当前体重 (kg)</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="14">
        <div class="card">
          <div class="card-header">
            <h3>记录训练</h3>
            <el-button type="primary" :icon="Plus" @click="showWorkoutDialog = true">
              添加打卡
            </el-button>
          </div>
          <div class="today-workouts">
            <div v-if="todayWorkouts.length === 0" class="empty-state">
              <el-icon :size="48" color="#c0c4cc"><Document /></el-icon>
              <p>今天还没有训练记录，开始你的第一次打卡吧！</p>
            </div>
            <div v-else>
              <div
                v-for="workout in todayWorkouts"
                :key="workout.id"
                class="workout-item"
              >
                <div class="workout-icon">
                  <el-tag :type="getWorkoutTypeColor(workout.workout_type)" size="large">
                    {{ workout.workout_type }}
                  </el-tag>
                </div>
                <div class="workout-info">
                  <div class="workout-meta">
                    <span v-if="workout.duration">
                      <el-icon><Clock /></el-icon>
                      {{ workout.duration }} 分钟
                    </span>
                    <span v-if="workout.calories">
                      <el-icon><Star /></el-icon>
                      {{ workout.calories }} 千卡
                    </span>
                  </div>
                  <div v-if="workout.notes" class="workout-notes">{{ workout.notes }}</div>
                </div>
                <div class="workout-actions">
                  <el-button type="danger" text :icon="Delete" @click="deleteWorkout(workout.id)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :span="10">
        <div class="card">
          <div class="card-header">
            <h3>记录体重</h3>
            <el-button type="success" :icon="Plus" @click="showWeightDialog = true">
              记录体重
            </el-button>
          </div>
          <div class="weight-section">
            <div v-if="latestWeight" class="weight-display">
              <div class="weight-value">{{ latestWeight.weight.toFixed(1) }}<span class="weight-unit">kg</span></div>
              <div class="weight-date">{{ latestWeight.date }}</div>
              <div v-if="stats.weight_change !== null" class="weight-change" :class="stats.weight_change < 0 ? 'down' : 'up'">
                <el-icon v-if="stats.weight_change < 0"><ArrowDown /></el-icon>
                <el-icon v-else><ArrowUp /></el-icon>
                {{ Math.abs(stats.weight_change).toFixed(1) }} kg 较首次
              </div>
            </div>
            <div v-else class="empty-state">
              <el-icon :size="48" color="#c0c4cc"><DataLine /></el-icon>
              <p>还没有体重记录</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>本周训练</h3>
          </div>
          <div ref="weeklyChartRef" class="weekly-chart"></div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="showWorkoutDialog" title="添加训练打卡" width="500px">
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
        <el-button @click="showWorkoutDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitWorkout">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showWeightDialog" title="记录体重" width="400px">
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
      </el-form>
      <template #footer>
        <el-button @click="showWeightDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitWeight">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Clock, Star, Delete, Document, DataLine,
  ArrowUp, ArrowDown
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { getWorkouts, createWorkout, deleteWorkout } from '@/api/workout'
import { getWeightRecords, createWeightRecord } from '@/api/weight'
import { getStats } from '@/api/stats'

const today = dayjs().format('YYYY-MM-DD')
const stats = ref({})
const todayWorkouts = ref([])
const latestWeight = ref(null)
const showWorkoutDialog = ref(false)
const showWeightDialog = ref(false)
const submitting = ref(false)
const weeklyChartRef = ref(null)
let weeklyChart = null

const workoutForm = ref({
  date: today,
  workout_type: '',
  duration: 30,
  calories: null,
  notes: ''
})

const weightForm = ref({
  date: today,
  weight: 60,
  body_fat: null
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

const loadData = async () => {
  try {
    const [workoutsRes, weightRes, statsRes] = await Promise.all([
      getWorkouts({ start_date: dayjs().subtract(7, 'day').format('YYYY-MM-DD') }),
      getWeightRecords({ limit: 10 }),
      getStats()
    ])

    todayWorkouts.value = workoutsRes.filter(w => w.date === today)
    latestWeight.value = weightRes[0] || null
    stats.value = statsRes

    await nextTick()
    renderWeeklyChart()
  } catch (err) {
    console.error('加载数据失败', err)
  }
}

const renderWeeklyChart = () => {
  if (!weeklyChartRef.value) return

  if (!weeklyChart) {
    weeklyChart = echarts.init(weeklyChartRef.value)
  }

  const days = []
  const data = []
  for (let i = 6; i >= 0; i--) {
    const d = dayjs().subtract(i, 'day')
    days.push(d.format('MM-DD'))
    const dayStat = stats.value.weekly_data?.find(item => item.date === d.format('YYYY-MM-DD'))
    data.push(dayStat?.duration || 0)
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>训练时长: {c} 分钟'
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
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', fontSize: 12 }
    },
    series: [{
      data: data,
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      }
    }]
  }

  weeklyChart.setOption(option)
}

const submitWorkout = async () => {
  if (!workoutForm.value.workout_type) {
    ElMessage.warning('请选择训练类型')
    return
  }

  try {
    submitting.value = true
    await createWorkout(workoutForm.value)
    ElMessage.success('打卡成功！')
    showWorkoutDialog.value = false
    workoutForm.value = {
      date: today,
      workout_type: '',
      duration: 30,
      calories: null,
      notes: ''
    }
    loadData()
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const submitWeight = async () => {
  try {
    submitting.value = true
    await createWeightRecord(weightForm.value)
    ElMessage.success('体重记录已保存！')
    showWeightDialog.value = false
    loadData()
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
    loadData()
  } catch (err) {
    if (err !== 'cancel') {
      console.error(err)
    }
  }
}

onMounted(() => {
  loadData()

  window.addEventListener('resize', () => {
    weeklyChart?.resize()
  })
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-state p {
  margin-top: 10px;
}

.workout-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f2f5;
}

.workout-item:last-child {
  border-bottom: none;
}

.workout-icon {
  margin-right: 15px;
}

.workout-info {
  flex: 1;
}

.workout-meta {
  display: flex;
  gap: 20px;
  color: #606266;
  font-size: 14px;
  margin-top: 8px;
}

.workout-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.workout-notes {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.weight-section {
  padding: 10px 0;
}

.weight-display {
  text-align: center;
  padding: 20px 0;
}

.weight-value {
  font-size: 48px;
  font-weight: 700;
  color: #67c23a;
}

.weight-unit {
  font-size: 20px;
  font-weight: 400;
  margin-left: 5px;
}

.weight-date {
  color: #909399;
  font-size: 14px;
  margin-top: 5px;
}

.weight-change {
  margin-top: 10px;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.weight-change.down {
  color: #67c23a;
}

.weight-change.up {
  color: #f56c6c;
}

.weekly-chart {
  height: 200px;
  width: 100%;
}
</style>
