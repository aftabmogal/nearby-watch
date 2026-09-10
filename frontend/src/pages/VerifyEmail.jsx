import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const RESEND_COOLDOWN = 30

export default function VerifyEmail() {
  const { verifyEmail, resendOtp } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const email = location.state?.email
  const name = location.state?.name

  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(false)
  const [cooldown, setCooldown] = useState(0)
  const timerRef = useRef(null)

  useEffect(() => {
    if (cooldown <= 0) return
    timerRef.current = setTimeout(() => setCooldown((c) => c - 1), 1000)
    return () => clearTimeout(timerRef.current)
  }, [cooldown])

  if (!email) {
    return (
      <div className="max-w-sm mx-auto px-5 py-16 text-center">
        <p className="text-ink/60 mb-4">
          We don't have an email to verify. Please register or log in again.
        </p>
        <Link to="/register" className="text-teal font-medium hover:underline">
          Back to sign up
        </Link>
      </div>
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await verifyEmail({ email, code, name })
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid code. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handleResend() {
    setError('')
    setInfo('')
    try {
      await resendOtp({ email, purpose: 'registration' })
      setInfo('A new code has been sent.')
      setCooldown(RESEND_COOLDOWN)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not resend code.')
    }
  }

  return (
    <div className="max-w-sm mx-auto px-5 py-16">
      <h1 className="font-display text-3xl font-semibold mb-1">Verify your email</h1>
      <p className="text-ink/60 mb-8">
        We sent a 6-digit code to <strong className="text-ink">{email}</strong>.
        {' '}(Local dev: check your backend terminal — codes print there via the console email provider.)
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="code">Verification code</label>
          <input
            id="code"
            type="text"
            inputMode="numeric"
            maxLength={6}
            required
            className="w-full border border-line rounded px-3 py-2 bg-white text-center text-2xl tracking-[0.5em] focus:border-teal outline-none"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
          />
        </div>

        {error && <p className="text-sm text-clay">{error}</p>}
        {info && <p className="text-sm text-sage">{info}</p>}

        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className="w-full bg-teal text-white rounded py-2.5 font-medium hover:bg-teal-dark transition-colors disabled:opacity-60"
        >
          {loading ? 'Verifying…' : 'Verify'}
        </button>
      </form>

      <button
        onClick={handleResend}
        disabled={cooldown > 0}
        className="text-sm text-teal font-medium hover:underline mt-6 disabled:text-ink/40 disabled:no-underline"
      >
        {cooldown > 0 ? `Resend code in ${cooldown}s` : 'Resend code'}
      </button>
    </div>
  )
}
