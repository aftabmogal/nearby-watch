import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import L from 'leaflet'
import { createPost } from '../api/posts'
import { POST_TYPES } from '../components/postMeta'

const DEFAULT_CENTER = [19.076, 72.8777]

const pinIcon = L.divIcon({
  className: '',
  html: `<div style="width:16px;height:16px;border-radius:50%;background:#B5533C;border:3px solid white;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
})

function LocationPicker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng])
    },
  })
  return position ? <Marker position={position} icon={pinIcon} /> : null
}

export default function CreatePost() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    type: 'lost_pet',
    title: '',
    description: '',
    addressLabel: '',
  })
  const [position, setPosition] = useState(null)
  const [photos, setPhotos] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!navigator.geolocation) {
      setPosition(DEFAULT_CENTER)
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setPosition([pos.coords.latitude, pos.coords.longitude]),
      () => setPosition(DEFAULT_CENTER),
      { timeout: 8000 }
    )
  }, [])

  function handlePhotoChange(e) {
    const files = Array.from(e.target.files || [])
    if (files.length > 3) {
      setError('Maximum 3 photos allowed.')
      return
    }
    setError('')
    setPhotos(files)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!position) {
      setError('Please wait for the map to load, or tap the map to set a location.')
      return
    }
    setLoading(true)
    try {
      const post = await createPost({
        type: form.type,
        title: form.title,
        description: form.description,
        latitude: position[0],
        longitude: position[1],
        addressLabel: form.addressLabel,
        photos,
      })
      navigate(`/posts/${post.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create post. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-5 py-8">
      <h1 className="font-display text-3xl font-semibold mb-1">Post something</h1>
      <p className="text-ink/60 mb-8">Neighbors within range will see this right away.</p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium mb-2">Type</label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {Object.entries(POST_TYPES).map(([key, meta]) => (
              <button
                type="button"
                key={key}
                onClick={() => setForm({ ...form, type: key })}
                className={`rounded border px-3 py-2 text-sm font-medium text-left transition-colors ${
                  form.type === key ? 'border-teal ring-1 ring-teal' : 'border-line bg-white'
                }`}
                style={form.type === key ? { backgroundColor: meta.bg, color: meta.color } : {}}
              >
                {meta.icon} {meta.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="title">Title</label>
          <input
            id="title"
            required
            maxLength={150}
            className="w-full border border-line rounded px-3 py-2 bg-white focus:border-teal outline-none"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="e.g. Lost golden retriever near the park"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="description">Description</label>
          <textarea
            id="description"
            required
            rows={4}
            maxLength={2000}
            className="w-full border border-line rounded px-3 py-2 bg-white focus:border-teal outline-none resize-none"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Add details that would help someone recognize this — color, markings, time seen, etc."
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="addressLabel">
            Landmark <span className="text-ink/40 font-normal">(optional)</span>
          </label>
          <input
            id="addressLabel"
            maxLength={150}
            className="w-full border border-line rounded px-3 py-2 bg-white focus:border-teal outline-none"
            value={form.addressLabel}
            onChange={(e) => setForm({ ...form, addressLabel: e.target.value })}
            placeholder="e.g. Near Bandra Bandstand"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Location <span className="text-ink/40 font-normal">— tap the map to adjust</span>
          </label>
          <div className="h-64 rounded border border-line overflow-hidden">
            {position && (
              <MapContainer center={position} zoom={14} className="w-full h-full">
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <LocationPicker position={position} setPosition={setPosition} />
              </MapContainer>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="photos">
            Photos <span className="text-ink/40 font-normal">(up to 3, optional)</span>
          </label>
          <input
            id="photos"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            onChange={handlePhotoChange}
            className="w-full text-sm"
          />
          {photos.length > 0 && (
            <div className="flex gap-2 mt-2">
              {photos.map((file, i) => (
                <img
                  key={i}
                  src={URL.createObjectURL(file)}
                  alt=""
                  className="w-16 h-16 object-cover rounded border border-line"
                />
              ))}
            </div>
          )}
        </div>

        {error && <p className="text-sm text-clay">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-teal text-white rounded py-2.5 font-medium hover:bg-teal-dark transition-colors disabled:opacity-60"
        >
          {loading ? 'Posting…' : 'Post'}
        </button>
      </form>
    </div>
  )
}
