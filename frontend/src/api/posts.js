import client from './client'

export async function createPost({ type, title, description, latitude, longitude, addressLabel, photos }) {
  const form = new FormData()
  form.append('type', type)
  form.append('title', title)
  form.append('description', description)
  form.append('latitude', latitude)
  form.append('longitude', longitude)
  if (addressLabel) form.append('address_label', addressLabel)
  ;(photos || []).forEach((file) => form.append('photos', file))

  const { data } = await client.post('/posts/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getNearbyPosts({ lat, lng, radiusKm = 5, type, status = 'active', skip = 0, limit = 50 }) {
  const params = { lat, lng, radius_km: radiusKm, status, skip, limit }
  if (type) params.type = type
  const { data } = await client.get('/posts/nearby', { params })
  return data
}

export async function getPost(postId) {
  const { data } = await client.get(`/posts/${postId}`)
  return data
}

export async function updatePost(postId, payload) {
  const { data } = await client.patch(`/posts/${postId}`, payload)
  return data
}

export async function reportPost(postId) {
  const { data } = await client.post(`/posts/${postId}/report`)
  return data
}

export async function getMyPosts() {
  const { data } = await client.get('/posts/mine/list')
  return data
}
