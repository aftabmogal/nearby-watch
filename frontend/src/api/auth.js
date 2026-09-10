import client, { setTokens, clearTokens } from './client'

export async function register({ email, name, password }) {
  const { data } = await client.post('/auth/register', { email, name, password })
  return data
}

export async function verifyEmail({ email, code }) {
  const { data } = await client.post('/auth/verify-email', { email, code })
  setTokens(data)
  return data
}

export async function resendOtp({ email, purpose = 'registration' }) {
  const { data } = await client.post('/auth/resend-otp', { email, purpose })
  return data
}

export async function login({ email, password }) {
  const { data } = await client.post('/auth/login', { email, password })
  setTokens(data)
  return data
}

export async function forgotPassword({ email }) {
  const { data } = await client.post('/auth/forgot-password', { email })
  return data
}

export async function resetPassword({ email, code, new_password }) {
  const { data } = await client.post('/auth/reset-password', { email, code, new_password })
  return data
}

export function logout() {
  clearTokens()
}
