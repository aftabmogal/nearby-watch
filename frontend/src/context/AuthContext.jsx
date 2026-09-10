import { createContext, useContext, useEffect, useState } from 'react'
import client, { getAccessToken, clearTokens } from '../api/client'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

const USER_KEY = 'lf_user'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem(USER_KEY)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  })
  const [ready, setReady] = useState(false)

  useEffect(() => {
    // We don't have a /me endpoint in this MVP, so we trust the locally
    // cached user object as long as an access token is present.
    const token = getAccessToken()
    if (!token) {
      setUser(null)
      localStorage.removeItem(USER_KEY)
    }
    setReady(true)
  }, [])

  function persistUser(email, name) {
    const u = { email, name }
    setUser(u)
    localStorage.setItem(USER_KEY, JSON.stringify(u))
  }

  async function register({ email, name, password }) {
    return authApi.register({ email, name, password })
  }

  async function verifyEmail({ email, code, name }) {
    await authApi.verifyEmail({ email, code })
    persistUser(email, name)
  }

  async function login({ email, password, name }) {
    await authApi.login({ email, password })
    persistUser(email, name || user?.name || email.split('@')[0])
  }

  function logout() {
    clearTokens()
    localStorage.removeItem(USER_KEY)
    setUser(null)
  }

  const value = {
    user,
    ready,
    isAuthenticated: Boolean(user && getAccessToken()),
    register,
    verifyEmail,
    login,
    logout,
    resendOtp: authApi.resendOtp,
    forgotPassword: authApi.forgotPassword,
    resetPassword: authApi.resetPassword,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

// Exported so other modules (e.g. the websocket context) can react to auth
// changes without importing the whole client module directly.
export { client }
