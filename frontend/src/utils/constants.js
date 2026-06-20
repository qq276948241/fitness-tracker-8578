export const WORKOUT_TYPES = [
  '力量训练',
  '有氧训练',
  'HIIT',
  '瑜伽',
  '跑步',
  '游泳',
  '骑行',
  '其他'
]

export const WORKOUT_TYPE_COLORS = {
  '力量训练': '',
  '有氧训练': 'success',
  'HIIT': 'warning',
  '瑜伽': 'info',
  '跑步': 'success',
  '游泳': 'primary',
  '骑行': '',
  '其他': 'info'
}

export function getWorkoutTypeColor(type) {
  return WORKOUT_TYPE_COLORS[type] || ''
}

export function formatWeight(weight) {
  if (weight === null || weight === undefined || weight === '') return '--'
  return Number(weight).toFixed(1)
}

export function formatDuration(minutes) {
  if (!minutes) return '0'
  return String(minutes)
}
