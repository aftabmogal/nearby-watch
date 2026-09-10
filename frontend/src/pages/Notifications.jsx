import { Link } from 'react-router-dom'
import { useNotifications } from '../context/NotificationContext'
import { formatRelativeTime } from '../components/postMeta'

export default function Notifications() {
  const { notifications, unreadCount, markAllAsRead } = useNotifications()

  return (
    <div className="max-w-2xl mx-auto px-5 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-2xl font-semibold">Alerts</h1>
        {unreadCount > 0 && (
          <button onClick={markAllAsRead} className="text-sm text-teal font-medium hover:underline">
            Mark all as read
          </button>
        )}
      </div>

      {notifications.length === 0 && (
        <div className="text-center py-16 border border-dashed border-line rounded">
          <p className="text-ink/60 font-medium">No alerts yet.</p>
          <p className="text-ink/45 text-sm mt-1">
            You'll be notified here when something is posted nearby or someone comments on your post.
          </p>
        </div>
      )}

      <div className="space-y-2">
        {notifications.map((n) => (
          <Link
            key={n.id}
            to={`/posts/${n.post_id}`}
            className={`block border rounded px-4 py-3 transition-colors ${
              n.is_read ? 'border-line bg-white' : 'border-teal bg-teal-soft'
            }`}
          >
            <p className="text-sm text-ink">{n.message}</p>
            <p className="text-xs text-ink/45 mt-1">{formatRelativeTime(n.created_at)}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
