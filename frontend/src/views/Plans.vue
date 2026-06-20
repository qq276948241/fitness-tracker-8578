<template>
  <div class="plans-page">
    <h2 class="page-title">训练计划</h2>

    <div class="card">
      <div class="card-header">
        <h3>推荐计划模板</h3>
      </div>

      <el-row :gutter="20">
        <el-col :span="8" v-for="plan in templatePlans" :key="plan.id">
          <div class="plan-card">
            <div class="plan-header">
              <el-icon :size="32" :color="plan.color"><List /></el-icon>
              <span class="plan-tag">模板</span>
            </div>
            <h4 class="plan-name">{{ plan.name }}</h4>
            <p class="plan-desc">{{ plan.description }}</p>
            <div class="plan-meta" v-if="plan.parsedData">
              <span><el-icon><Clock /></el-icon> 每次 {{ plan.parsedData.duration }} 分钟</span>
              <span><el-icon><Refresh /></el-icon> 每周 {{ plan.parsedData.frequency }} 次</span>
              <el-tag size="small" :type="getLevelType(plan.parsedData.level)">
                {{ plan.parsedData.level }}
              </el-tag>
            </div>
            <div class="plan-exercises" v-if="plan.parsedData?.exercises">
              <span class="exercise-label">主要动作：</span>
              <span class="exercise-list">
                {{ plan.parsedData.exercises.join('、') }}
              </span>
            </div>
            <el-button type="primary" class="use-plan-btn" @click="usePlan(plan)">
              使用此计划
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="card">
      <div class="card-header">
        <h3>我的计划</h3>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          创建计划
        </el-button>
      </div>

      <el-empty v-if="myPlans.length === 0" description="还没有创建自己的计划" />

      <el-row :gutter="20" v-else>
        <el-col :span="8" v-for="plan in myPlans" :key="plan.id">
          <div class="plan-card my-plan">
            <h4 class="plan-name">{{ plan.name }}</h4>
            <p class="plan-desc">{{ plan.description || '暂无描述' }}</p>
            <div class="plan-actions">
              <el-button size="small" text type="primary">查看</el-button>
              <el-button size="small" text type="danger">删除</el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="showCreateDialog" title="创建训练计划" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="计划名称">
          <el-input v-model="createForm.name" placeholder="给你的计划起个名字" />
        </el-form-item>
        <el-form-item label="计划描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="2"
            placeholder="简单描述一下这个计划"
          />
        </el-form-item>
        <el-form-item label="训练频率">
          <el-input-number v-model="createForm.frequency" :min="1" :max="7" />
          <span style="margin-left: 10px; color: #909399">次/周</span>
        </el-form-item>
        <el-form-item label="每次时长">
          <el-input-number v-model="createForm.duration" :min="10" :max="180" />
          <span style="margin-left: 10px; color: #909399">分钟</span>
        </el-form-item>
        <el-form-item label="难度等级">
          <el-select v-model="createForm.level" style="width: 100%">
            <el-option label="初级" value="初级" />
            <el-option label="中级" value="中级" />
            <el-option label="高级" value="高级" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createPlan">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus, List, Clock, Refresh
} from '@element-plus/icons-vue'
import { getPlans, createPlan as apiCreatePlan } from '@/api/stats'

const plans = ref([])
const showCreateDialog = ref(false)
const creating = ref(false)

const createForm = ref({
  name: '',
  description: '',
  frequency: 3,
  duration: 45,
  level: '初级'
})

const templatePlans = computed(() => {
  return plans.value.filter(p => p.is_template === 1).map(p => ({
    ...p,
    parsedData: p.plan_data ? JSON.parse(p.plan_data) : null,
    color: getPlanColor(p.id)
  }))
})

const myPlans = computed(() => {
  return plans.value.filter(p => p.is_template === 0)
})

const getPlanColor = (id) => {
  const colors = ['#667eea', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
  return colors[id % colors.length]
}

const getLevelType = (level) => {
  const types = {
    '初级': 'success',
    '中级': 'warning',
    '高级': 'danger'
  }
  return types[level] || ''
}

const loadPlans = async () => {
  try {
    const res = await getPlans({ include_templates: true })
    plans.value = res
  } catch (err) {
    console.error(err)
  }
}

const usePlan = (plan) => {
  ElMessage.success(`已选择「${plan.name}」，快去打卡吧！`)
}

const createPlan = async () => {
  if (!createForm.value.name) {
    ElMessage.warning('请输入计划名称')
    return
  }

  try {
    creating.value = true
    const planData = {
      frequency: createForm.value.frequency,
      duration: createForm.value.duration,
      level: createForm.value.level,
      exercises: []
    }
    await apiCreatePlan({
      name: createForm.value.name,
      description: createForm.value.description,
      plan_data: JSON.stringify(planData)
    })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    createForm.value = {
      name: '',
      description: '',
      frequency: 3,
      duration: 45,
      level: '初级'
    }
    loadPlans()
  } catch (err) {
    console.error(err)
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadPlans()
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

.plan-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 2px solid transparent;
  transition: all 0.3s;
  position: relative;
}

.plan-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.plan-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.plan-tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.plan-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.plan-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  min-height: 40px;
}

.plan-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 15px;
  font-size: 13px;
  color: #606266;
}

.plan-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.plan-exercises {
  font-size: 13px;
  color: #909399;
  margin-bottom: 15px;
  line-height: 1.5;
}

.exercise-label {
  color: #606266;
}

.use-plan-btn {
  width: 100%;
}

.my-plan {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.plan-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
</style>
