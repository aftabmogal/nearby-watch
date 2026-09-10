import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMyPosts } from '../api/posts'
import PostCard from '../components/PostCard'

export default function MyPosts() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getMyPosts()
      .then(setPosts)
      .catch(() => setError('Could not load your posts.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-5 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-2xl font-semibold">My posts</h1>
        <Link
          to="/create"
          className="px-4 py-2 text-sm font-medium rounded bg-teal text-white hover:bg-teal-dark"
        >
          New post
        </Link>
      </div>

      {loading && <p className="text-ink/50 text-sm">Loading…</p>}
      {error && <p className="text-sm text-clay">{error}</p>}

      {!loading && posts.length === 0 && (
        <div className="text-center py-16 border border-dashed border-line rounded">
          <p className="text-ink/60 font-medium">You haven't posted anything yet.</p>
          <Link to="/create" className="text-teal font-medium hover:underline text-sm mt-1 inline-block">
            Create your first post
          </Link>
        </div>
      )}

      <div className="space-y-3">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  )
}
