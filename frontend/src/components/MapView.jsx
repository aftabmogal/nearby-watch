import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'
import L from 'leaflet'
import { useNavigate } from 'react-router-dom'
import { typeMeta } from './postMeta'

// Leaflet's default marker icons reference image paths that don't resolve
// correctly through Vite's bundler — build custom divIcons instead so we
// don't depend on Leaflet's default marker assets at all.
function buildIcon(type) {
  const meta = typeMeta(type)
  return L.divIcon({
    className: '',
    html: `<div class="marker-pin" style="background:${meta.color}"><span>${meta.icon}</span></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28],
  })
}

function RecenterOnChange({ center }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, map.getZoom())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [center[0], center[1]])
  return null
}

export default function MapView({ center, radiusKm, posts }) {
  const navigate = useNavigate()

  return (
    <MapContainer center={center} zoom={13} className="w-full h-full" scrollWheelZoom>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <RecenterOnChange center={center} />

      <Circle
        center={center}
        radius={radiusKm * 1000}
        pathOptions={{ color: '#1F5C52', fillColor: '#1F5C52', fillOpacity: 0.06, weight: 1 }}
      />

      <Marker
        position={center}
        icon={L.divIcon({
          className: '',
          html: `<div style="width:14px;height:14px;border-radius:50%;background:#1F5C52;border:3px solid white;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div>`,
          iconSize: [14, 14],
          iconAnchor: [7, 7],
        })}
      >
        <Popup>You are here (approximately)</Popup>
      </Marker>

      {posts.map((post) => (
        <Marker
          key={post.id}
          position={[post.latitude, post.longitude]}
          icon={buildIcon(post.type)}
          eventHandlers={{ click: () => navigate(`/posts/${post.id}`) }}
        >
          <Popup>
            <div className="text-sm">
              <strong>{post.title}</strong>
              <div className="text-ink/60">{typeMeta(post.type).label}</div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
