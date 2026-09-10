import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNotifications } from '../context/NotificationContext'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const { unreadCount } = useNotifications()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-40 bg-paper/95 backdrop-blur border-b border-line">
      <div className="max-w-6xl mx-auto px-5 h-16 flex items-center justify-between">
        <Link to="/" className="font-display text-xl font-semibold text-teal-dark">
          Nearby Watch
        </Link>

        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            to="/"
            className="px-3 py-2 text-sm font-medium rounded hover:bg-teal-soft transition-colors"
          >
            Browse
          </Link>

          {isAuthenticated && (
            <>
              <Link
                to="/create"
                className="px-3 py-2 text-sm font-medium rounded hover:bg-teal-soft transition-colors"
              >
                Post
              </Link>
              <Link
                to="/my-posts"
                className="px-3 py-2 text-sm font-medium rounded hover:bg-teal-soft transition-colors"
              >
                My posts
              </Link>
              <Link
                to="/notifications"
                className="relative px-3 py-2 text-sm font-medium rounded hover:bg-teal-soft transition-colors"
              >
                Alerts
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full bg-clay text-white text-[11px] leading-[18px] text-center font-semibold">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Link>
              <span className="hidden sm:inline text-sm text-ink/50 px-2">{user?.name}</span>
              <button
                onClick={handleLogout}
                className="px-3 py-2 text-sm font-medium rounded border border-line hover:bg-white transition-colors"
              >
                Log out
              </button>
            </>
          )}

          {!isAuthenticated && (
            <>
              <Link
                to="/login"
                className="px-3 py-2 text-sm font-medium rounded hover:bg-teal-soft transition-colors"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="px-3 py-2 text-sm font-medium rounded bg-teal text-white hover:bg-teal-dark transition-colors"
              >
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
