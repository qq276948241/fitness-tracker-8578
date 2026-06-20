import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, getProfile } from '@/api/auth'
import { useStatsStore } from './stats'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  const setAuth = (tokenValue, userData) => {
    token.value = tokenValue
    user.value = userData
    localStorage.setItem('token', tokenValue)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const clearAuth = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const login = async (username, password) => {
    const res = await apiLogin(username, password)
    setAuth(res.access_token, res.user)
    return res
  }

  const register = async (userData) => {
    const res = await apiRegister(userData)
    setAuth(res.access_token, res.user)
    return res
  }

  const logout = () => {
    clearAuth()
    const statsStore = useStatsStore()
    statsStore.$reset()
  }

  const checkAuth = async () => {
    if (token.value) {
      try {
        const res = await getProfile()
        user.value = res
        localStorage.setItem('user', JSON.stringify(res))
      } catch (err) {
        clearAuth()
        const statsStore = useStatsStore()
        statsStore.$reset()
      }
    }
  }

  const updateUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    logout,
    checkAuth,
    updateUser
  }
})
