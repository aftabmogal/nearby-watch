import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { WS_URL, getAccessToken } from '../api/client'
import { getUnreadCount, listNotifications, markAllRead } from '../api/notifications'
import { useAuth } from './AuthContext'

const NotificationContext = createContext(null)

export function NotificationProvider({ children }) {
  const { isAuthenticated } = useAuth()
  const [toasts, setToasts] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [notifications, setNotifications] = useState([])
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const pushToast = useCallback((message) => {
    const id = crypto.randomUUID()
    setToasts((prev) => [...prev, { id, message }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 6000)
  }, [])

  const refreshUnreadCount = useCallback(async () => {
    if (!isAuthenticated) return
    try {
      const count = await getUnreadCount()
      setUnreadCount(count)
    } catch {
      // silent — notification badge is non-critical
    }
  }, [isAuthenticated])

  const refreshNotifications = useCallback(async () => {
    if (!isAuthenticated) return
    try {
      const list = await listNotifications()
      setNotifications(list)
    } catch {
      // silent
    }
  }, [isAuthenticated])

  const markAllAsRead = useCallback(async () => {
    try {
      await markAllRead()
      setUnreadCount(0)
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    } catch {
      // silent
    }
  }, [])

  // Share the browser's current position with the server over the socket,
  // so the server knows who's "nearby" for a new post. Best-effort only —
  // if geolocation is denied, the user simply won't get live pushes (the
  // rest of the app still works fine via the persisted Notification list).
  const sendLocation = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        wsRef.current?.send(
          JSON.stringify({
            type: 'location',
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
          })
        )
      },
      () => {},
      { maximumAge: 60000, timeout: 5000 }
    )
  }, [])

  useEffect(() => {
    if (!isAuthenticated) {
      wsRef.current?.close()
      return
    }

    refreshUnreadCount()
    refreshNotifications()

    function connect() {
      const token = getAccessToken()
      if (!token) return
      const ws = new WebSocket(`${WS_URL}/ws/notifications?token=${token}`)
      wsRef.current = ws

      ws.onopen = () => {
        sendLocation()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          pushToast(data.message)
          setUnreadCount((c) => c + 1)
          refreshNotifications()
        } catch {
          // ignore malformed messages
        }
      }

      ws.onclose = () => {
        // Auto-reconnect after a short delay — acceptable for a single-process
        // in-memory MVP; see backend/app/services/ws_manager.py for the note
        // on scaling this to Redis pub/sub later.
        reconnectTimer.current = setTimeout(connect, 4000)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated])

  const value = {
    toasts,
    unreadCount,
    notifications,
    refreshNotifications,
    markAllAsRead,
  }

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>
}

export function useNotifications() {
  const ctx = useContext(NotificationContext)
  if (!ctx) throw new Error('useNotifications must be used within NotificationProvider')
  return ctx
}
