<template>
  <div class="settings-page">
    <h2 class="page-title">个人设置</h2>

    <el-row :gutter="20">
      <el-col :span="16">
        <div class="card">
          <h3 class="section-title">基本信息</h3>
          <el-form :model="form" label-width="100px" style="max-width: 500px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.full_name" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="身高">
              <el-input-number v-model="form.height" :min="100" :max="250" :step="0.1" />
              <span style="margin-left: 10px; color: #909399">cm</span>
            </el-form-item>
            <el-form-item label="目标体重">
              <el-input-number v-model="form.target_weight" :min="30" :max="200" :step="0.5" />
              <span style="margin-left: 10px; color: #909399">kg</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveProfile">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="card">
          <h3 class="section-title">修改密码</h3>
          <el-form :model="passwordForm" label-width="100px" style="max-width: 500px">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="changingPwd" @click="changePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="card">
          <h3 class="section-title">我的数据</h3>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">累计训练</span>
              <span class="stat-value">{{ stats.total_workouts || 0 }} 次</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">累计时长</span>
              <span class="stat-value">{{ stats.total_duration || 0 }} 分钟</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">累计消耗</span>
              <span class="stat-value">{{ stats.total_calories || 0 }} 千卡</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">当前体重</span>
              <span class="stat-value">{{ stats.current_weight ? stats.current_weight.toFixed(1) : '--' }} kg</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">目标体重</span>
              <span class="stat-value">{{ stats.target_weight ? stats.target_weight.toFixed(1) : '未设置' }} {{ stats.target_weight ? 'kg' : '' }}</span>
            </div>
            <div class="stat-item" v-if="stats.target_weight && stats.current_weight">
              <span class="stat-label">距目标</span>
              <span class="stat-value" :class="stats.weight_to_target > 0 ? 'text-danger' : 'text-success'">
                {{ Math.abs(stats.weight_to_target).toFixed(1) }} kg {{ stats.weight_to_target > 0 ? '还需减' : '已达标' }}
              </span>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title">关于</h3>
          <div class="about-info">
            <p>健身打卡 v1.0.0</p>
            <p class="about-desc">
              一款帮助你记录训练、追踪体重、管理健身计划的小工具。
              坚持打卡，遇见更好的自己！💪
            </p>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useStatsStore } from '@/stores/stats'
import { updateProfile } from '@/api/auth'

const userStore = useUserStore()
const statsStore = useStatsStore()
const saving = ref(false)
const changingPwd = ref(false)

const stats = computed(() => statsStore.stats)

const form = ref({
  username: '',
  full_name: '',
  email: '',
  height: null,
  target_weight: null
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const loadUserInfo = () => {
  if (userStore.user) {
    form.value = {
      username: userStore.user.username,
      full_name: userStore.user.full_name || '',
      email: userStore.user.email,
      height: userStore.user.height || null,
      target_weight: userStore.user.target_weight || null
    }
  }
}

const saveProfile = async () => {
  try {
    saving.value = true
    const res = await updateProfile({
      username: form.value.username,
      full_name: form.value.full_name,
      email: form.value.email,
      height: form.value.height,
      target_weight: form.value.target_weight
    })
    userStore.updateUser(res)
    ElMessage.success('保存成功')
    statsStore.refreshStats()
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.value.old_password) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.value.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  ElMessage.info('密码修改功能暂未开放，敬请期待~')
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
}

onMounted(() => {
  loadUserInfo()
  statsStore.loadStats()
})
</script>

<style scoped>
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.about-info p {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.about-desc {
  margin-top: 10px;
}

.text-danger {
  color: #f56c6c;
}

.text-success {
  color: #67c23a;
}
</style>
