<template>
  <div id="app">
    <el-container v-if="isLoggedIn" class="main-container">
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <el-icon :size="28" color="#67c23a"><Trophy /></el-icon>
          <span class="logo-text">健身打卡</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          @select="handleMenuSelect"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/">
            <el-icon><Calendar /></el-icon>
            <span>今日打卡</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Clock /></el-icon>
            <span>历史记录</span>
          </el-menu-item>
          <el-menu-item index="/stats">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据统计</span>
          </el-menu-item>
          <el-menu-item index="/plans">
            <el-icon><List /></el-icon>
            <span>训练计划</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>个人设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <span class="welcome-text">欢迎回来，{{ userStore.user?.full_name || userStore.user?.username }}！</span>
          </div>
          <div class="header-right">
            <el-button type="primary" plain @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
    <div v-else class="login-page">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const activeMenu = computed(() => route.path)

onMounted(() => {
  userStore.checkAuth()
})

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-container {
  min-height: 100vh;
}

.sidebar {
  background: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid #1f2d3d;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.welcome-text {
  font-size: 16px;
  color: #606266;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}

.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
