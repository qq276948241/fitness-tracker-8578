import request from '@/utils/request'

export function getWeightRecords(params = {}) {
  return request.get('/weight', { params })
}

export function createWeightRecord(data) {
  return request.post('/weight', data)
}

export function updateWeightRecord(id, data) {
  return request.put(`/weight/${id}`, data)
}

export function deleteWeightRecord(id) {
  return request.delete(`/weight/${id}`)
}
