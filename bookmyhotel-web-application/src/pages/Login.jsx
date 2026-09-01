import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import './Auth.css'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  // if we were sent here from another page (like Select Room while logged
  // out), that page passes a message and a redirectTo path via navigate state
  const redirectMessage = location.state?.message
  const redirectTo = location.state?.redirectTo || '/'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    setLoading(false)

    if (error) {
      setError(error.message)
    } else {
      navigate(redirectTo)
    }
  }

  return (
    <div
      className="auth-page"
      style={{ backgroundImage: `url(https://images.unsplash.com/photo-1758194090785-8e09b7288199?w=1600&q=95&auto=format&fit=crop)` }}
    >
      <div className="auth-card">
        <h1>Every Stay Begins With a Return</h1>
        <p className="auth-subtitle">Log in to manage your bookings</p>

        {redirectMessage && <p className="auth-info">{redirectMessage}</p>}

        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>

          <label>
            Password
            <div className="password-input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
              </button>
            </div>
          </label>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Logging In...' : 'Log In'}
          </button>
        </form>

        <p className="auth-switch">
          Don't have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>
    </div>
  )
}

export default Login