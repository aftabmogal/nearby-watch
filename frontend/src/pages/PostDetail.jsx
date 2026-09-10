import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPost, updatePost, reportPost } from '../api/posts'
import { getComments, addComment } from '../api/comments'
import { useAuth } from '../context/AuthContext'
import { typeMeta, formatRelativeTime } from '../components/postMeta'

export default function PostDetail() {
  const { postId } = useParams()
  const { isAuthenticated } = useAuth()
  const [post, setPost] = useState(null)
  const [comments, setComments] = useState([])
  const [commentText, setCommentText] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')
  const [submittingComment, setSubmittingComment] = useState(false)

  async function loadAll() {
    setLoading(true)
    setError('')
    try {
      const [postData, commentsData] = await Promise.all([
        getPost(postId),
        getComments(postId),
      ])
      setPost(postData)
      setComments(commentsData)
    } catch {
      setError('This post could not be found.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [postId])

  async function handleAddComment(e) {
    e.preventDefault()
    if (!commentText.trim()) return
    setSubmittingComment(true)
    try {
      const comment = await addComment(postId, commentText.trim())
      setComments((prev) => [...prev, comment])
      setCommentText('')
    } catch {
      setActionMessage('Could not post your comment. Please try again.')
    } finally {
      setSubmittingComment(false)
    }
  }

  async function handleResolve() {
    try {
      const updated = await updatePost(postId, { status: 'resolved' })
      setPost(updated)
    } catch (err) {
      if (err.response?.status === 403) {
        setActionMessage('Only the person who posted this can mark it resolved.')
      } else {
        setActionMessage('Could not update the post.')
      }
    }
  }

  async function handleReport() {
    try {
      await reportPost(postId)
      setActionMessage('Thanks — this post has been flagged for review.')
    } catch {
      setActionMessage('Could not report this post.')
    }
  }

  if (loading) {
    return <div className="max-w-3xl mx-auto px-5 py-16 text-center text-ink/60">Loading…</div>
  }

  if (error || !post) {
    return (
      <div className="max-w-3xl mx-auto px-5 py-16 text-center">
        <p className="text-ink/60 mb-4">{error || 'Post not found.'}</p>
        <Link to="/" className="text-teal font-medium hover:underline">Back to browse</Link>
      </div>
    )
  }

  const meta = typeMeta(post.type)

  return (
    <div className="max-w-3xl mx-auto px-5 py-8">
      <Link to="/" className="text-sm text-teal hover:underline">&larr; Back to browse</Link>

      <div className="mt-4 flex items-center gap-2">
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded"
          style={{ color: meta.color, backgroundColor: meta.bg }}
        >
          {meta.icon} {meta.label}
        </span>
        {post.status === 'resolved' && (
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-sage-soft text-sage">
            Resolved
          </span>
        )}
      </div>

      <h1 className="font-display text-3xl font-semibold mt-3">{post.title}</h1>
      <p className="text-sm text-ink/45 mt-1">
        Posted by {post.author_name} &middot; {formatRelativeTime(post.created_at)}
        {post.address_label && <> &middot; {post.address_label}</>}
      </p>

      {post.photos?.length > 0 && (
        <div className="flex gap-2 mt-5 overflow-x-auto">
          {post.photos.map((url, i) => (
            <img key={i} src={url} alt="" className="h-64 rounded border border-line object-cover" />
          ))}
        </div>
      )}

      <p className="text-ink/80 leading-relaxed mt-5 whitespace-pre-wrap">{post.description}</p>

      {actionMessage && <p className="text-sm text-teal mt-4">{actionMessage}</p>}

      <div className="flex gap-2 mt-6">
        {isAuthenticated && post.status === 'active' && (
          <button
            onClick={handleResolve}
            className="px-4 py-2 text-sm font-medium rounded bg-sage text-white hover:opacity-90"
          >
            Mark as resolved
          </button>
        )}
        {isAuthenticated && (
          <button
            onClick={handleReport}
            className="px-4 py-2 text-sm font-medium rounded border border-line hover:bg-white"
          >
            Report
          </button>
        )}
      </div>

      <hr className="border-line my-8" />

      <h2 className="font-display text-xl font-semibold mb-4">
        Comments {comments.length > 0 && `(${comments.length})`}
      </h2>

      {isAuthenticated ? (
        <form onSubmit={handleAddComment} className="flex gap-2 mb-6">
          <input
            className="flex-1 border border-line rounded px-3 py-2 bg-white focus:border-teal outline-none"
            placeholder="Add a comment…"
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            maxLength={1000}
          />
          <button
            type="submit"
            disabled={submittingComment || !commentText.trim()}
            className="px-4 py-2 text-sm font-medium rounded bg-teal text-white hover:bg-teal-dark disabled:opacity-60"
          >
            Post
          </button>
        </form>
      ) : (
        <p className="text-sm text-ink/50 mb-6">
          <Link to="/login" className="text-teal hover:underline">Sign in</Link> to comment.
        </p>
      )}

      <div className="space-y-4">
        {comments.length === 0 && (
          <p className="text-sm text-ink/45">No comments yet — be the first to say something.</p>
        )}
        {comments.map((c) => (
          <div key={c.id} className="border-b border-line pb-3">
            <div className="flex items-baseline gap-2">
              <span className="font-medium text-sm">{c.author_name}</span>
              <span className="text-xs text-ink/40">{formatRelativeTime(c.created_at)}</span>
            </div>
            <p className="text-ink/80 text-sm mt-0.5">{c.text}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
