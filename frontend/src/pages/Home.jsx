import { useEffect, useMemo, useState } from 'react'
import { getNearbyPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import MapView from '../components/MapView'
import { POST_TYPES } from '../components/postMeta'

const RADIUS_OPTIONS = [1, 5, 10, 25]
const DEFAULT_CENTER = [19.076, 72.8777] // fallback if geolocation is denied — matches backend seed data

export default function Home() {
  const [center, setCenter] = useState(null)
  const [locationDenied, setLocationDenied] = useState(false)
  const [radiusKm, setRadiusKm] = useState(5)
  const [typeFilter, setTypeFilter] = useState('')
  const [view, setView] = useState('map') // 'map' | 'list'
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!navigator.geolocation) {
      setLocationDenied(true)
      setCenter(DEFAULT_CENTER)
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setCenter([pos.coords.latitude, pos.coords.longitude]),
      () => {
        setLocationDenied(true)
        setCenter(DEFAULT_CENTER)
      },
      { timeout: 8000 }
    )
  }, [])

  useEffect(() => {
    if (!center) return
    let cancelled = false
    setLoading(true)
    setError('')
    getNearbyPosts({ lat: center[0], lng: center[1], radiusKm, type: typeFilter || undefined })
      .then((data) => {
        if (!cancelled) setPosts(data)
      })
      .catch(() => {
        if (!cancelled) setError('Could not load nearby posts. Is the backend running?')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [center, radiusKm, typeFilter])

  const emptyState = useMemo(
    () => !loading && !error && posts.length === 0,
    [loading, error, posts]
  )

  if (!center) {
    return (
      <div className="max-w-6xl mx-auto px-5 py-16 text-center text-ink/60">
        Getting your location…
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-5 py-6">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <h1 className="font-display text-2xl font-semibold mr-auto">What's nearby</h1>

        <div className="flex items-center bg-white border border-line rounded overflow-hidden text-sm">
          <button
            onClick={() => setView('map')}
            className={`px-3 py-1.5 font-medium ${view === 'map' ? 'bg-teal text-white' : 'hover:bg-teal-soft'}`}
          >
            Map
          </button>
          <button
            onClick={() => setView('list')}
            className={`px-3 py-1.5 font-medium ${view === 'list' ? 'bg-teal text-white' : 'hover:bg-teal-soft'}`}
          >
            List
          </button>
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border border-line rounded px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All types</option>
          {Object.entries(POST_TYPES).map(([key, meta]) => (
            <option key={key} value={key}>{meta.label}</option>
          ))}
        </select>

        <div className="flex items-center gap-2 text-sm">
          <span className="text-ink/60">Radius</span>
          {RADIUS_OPTIONS.map((km) => (
            <button
              key={km}
              onClick={() => setRadiusKm(km)}
              className={`px-2.5 py-1 rounded border text-xs font-medium ${
                radiusKm === km
                  ? 'bg-teal text-white border-teal'
                  : 'border-line bg-white hover:bg-teal-soft'
              }`}
            >
              {km}km
            </button>
          ))}
        </div>
      </div>

      {locationDenied && (
        <p className="text-xs text-ink/50 mb-4">
          Using a default location since precise location wasn't available — showing the list view.
        </p>
      )}

      {error && (
        <div className="bg-clay-soft text-clay rounded px-4 py-3 text-sm mb-4">{error}</div>
      )}

      {view === 'map' && !locationDenied ? (
        <div className="h-[65vh] rounded border border-line overflow-hidden">
          <MapView center={center} radiusKm={radiusKm} posts={posts} />
        </div>
      ) : (
        <div className="space-y-3">
          {loading && <p className="text-ink/50 text-sm">Loading nearby posts…</p>}
          {emptyState && (
            <div className="text-center py-16 border border-dashed border-line rounded">
              <p className="text-ink/60 font-medium">No posts near you yet.</p>
              <p className="text-ink/45 text-sm mt-1">
                Try a wider radius, or be the first to post something in your area.
              </p>
            </div>
          )}
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}
