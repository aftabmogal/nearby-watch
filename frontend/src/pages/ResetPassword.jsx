import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ResetPassword() {
  const { resetPassword } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const email = location.state?.email

  const [form, setForm] = useState({ code: '', new_password: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  if (!email) {
    return (
      <div className="max-w-sm mx-auto px-5 py-16 text-center">
        <p className="text-ink/60 mb-4">Please request a reset code first.</p>
        <Link to="/forgot-password" className="text-teal font-medium hover:underline">
          Request a code
        </Link>
      </div>
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await resetPassword({ email, code: form.code, new_password: form.new_password })
      setSuccess(true)
      setTimeout(() => navigate('/login'), 1800)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not reset password.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="max-w-sm mx-auto px-5 py-16 text-center">
        <h1 className="font-display text-2xl font-semibold mb-2">Password reset</h1>
        <p className="text-ink/60">Taking you to sign in…</p>
      </div>
    )
  }

  return (
    <div className="max-w-sm mx-auto px-5 py-16">
      <h1 className="font-display text-3xl font-semibold mb-1">Enter your new password</h1>
      <p className="text-ink/60 mb-8">
        Code sent to <strong className="text-ink">{email}</strong>
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="code">Reset code</label>
          <input
            id="code"
            type="text"
            inputMode="numeric"
            maxLength={6}
            required
            className="w-full border border-line rounded px-3 py-2 bg-white text-center text-2xl tracking-[0.5em] focus:border-teal outline-none"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value.replace(/\D/g, '') })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="new_password">New password</label>
          <input
            id="new_password"
            type="password"
            minLength={8}
            required
            className="w-full border border-line rounded px-3 py-2 bg-white focus:border-teal outline-none"
            value={form.new_password}
            onChange={(e) => setForm({ ...form, new_password: e.target.value })}
          />
        </div>

        {error && <p className="text-sm text-clay">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-teal text-white rounded py-2.5 font-medium hover:bg-teal-dark transition-colors disabled:opacity-60"
        >
          {loading ? 'Resetting…' : 'Reset password'}
        </button>
      </form>
    </div>
  )
}
