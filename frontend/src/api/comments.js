import client from './client'

export async function getComments(postId) {
  const { data } = await client.get(`/posts/${postId}/comments/`)
  return data
}

export async function addComment(postId, text) {
  const { data } = await client.post(`/posts/${postId}/comments/`, { text })
  return data
}
