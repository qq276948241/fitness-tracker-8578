import request from '@/utils/request'

export function getWorkouts(params = {}) {
  return request.get('/workouts', { params })
}

export function getWorkout(id) {
  return request.get(`/workouts/${id}`)
}

export function createWorkout(data) {
  return request.post('/workouts', data)
}

export function updateWorkout(id, data) {
  return request.put(`/workouts/${id}`, data)
}

export function deleteWorkout(id) {
  return request.delete(`/workouts/${id}`)
}
