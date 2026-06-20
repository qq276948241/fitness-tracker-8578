import request from '@/utils/request'

export function getPlans(params = {}) {
  return request.get('/plans', { params })
}

export function createPlan(data) {
  return request.post('/plans', data)
}

export function getStats() {
  return request.get('/stats')
}
