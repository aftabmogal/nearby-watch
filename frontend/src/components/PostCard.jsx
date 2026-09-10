import { Link } from 'react-router-dom'
import { typeMeta, formatRelativeTime } from './postMeta'

export default function PostCard({ post }) {
  const meta = typeMeta(post.type)

  return (
    <Link
      to={`/posts/${post.id}`}
      className="flex gap-3 bg-white border border-line rounded overflow-hidden hover:shadow-md transition-shadow"
      style={{ borderLeftWidth: '4px', borderLeftColor: meta.color }}
    >
      {post.photos?.[0] ? (
        <img
          src={post.photos[0]}
          alt=""
          className="w-24 h-24 object-cover flex-shrink-0"
        />
      ) : (
        <div
          className="w-24 h-24 flex-shrink-0 flex items-center justify-center text-3xl"
          style={{ backgroundColor: meta.bg }}
        >
          {meta.icon}
        </div>
      )}

      <div className="py-3 pr-3 min-w-0 flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span
            className="text-xs font-semibold px-2 py-0.5 rounded"
            style={{ color: meta.color, backgroundColor: meta.bg }}
          >
            {meta.label}
          </span>
          {post.status === 'resolved' && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-sage-soft text-sage">
              Resolved
            </span>
          )}
        </div>
        <h3 className="font-medium text-ink truncate">{post.title}</h3>
        <p className="text-sm text-ink/60 truncate">{post.description}</p>
        <div className="flex items-center gap-2 text-xs text-ink/45 mt-1">
          {post.address_label && <span className="truncate">{post.address_label}</span>}
          {post.distance_km != null && (
            <>
              <span>&middot;</span>
              <span>{post.distance_km} km away</span>
            </>
          )}
          <span>&middot;</span>
          <span>{formatRelativeTime(post.created_at)}</span>
        </div>
      </div>
    </Link>
  )
}
