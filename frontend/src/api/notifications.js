import client from './client'

export async function listNotifications() {
  const { data } = await client.get('/notifications/')
  return data
}

export async function getUnreadCount() {
  const { data } = await client.get('/notifications/unread-count')
  return data.unread_count
}

export async function markNotificationRead(id) {
  const { data } = await client.patch(`/notifications/${id}/read`)
  return data
}

export async function markAllRead() {
  const { data } = await client.post('/notifications/read-all')
  return data
}
