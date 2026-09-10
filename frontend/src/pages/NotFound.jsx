import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="max-w-md mx-auto px-5 py-24 text-center">
      <h1 className="font-display text-3xl font-semibold mb-2">Page not found</h1>
      <p className="text-ink/60 mb-8">That page doesn't exist or may have moved.</p>
      <Link to="/" className="text-teal font-medium hover:underline">Back to browse</Link>
    </div>
  )
}
