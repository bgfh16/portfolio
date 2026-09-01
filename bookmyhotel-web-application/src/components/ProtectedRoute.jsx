import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

// wraps any page that requires login (and optionally, admin access)
// if not logged in, redirects to login with a message and a way back
// if adminOnly is true and the user isn't an admin, redirects home
function ProtectedRoute({ children, adminOnly = false }) {
  const { user, isAdmin, loading } = useAuth()
  const location = useLocation()

  // wait until we know the real auth state before deciding anything,
  // otherwise we might redirect someone who is actually logged in
  if (loading) {
    return <p style={{ textAlign: 'center', padding: '48px 0' }}>Loading...</p>
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        state={{
          message: 'Please log in to access this page.',
          redirectTo: location.pathname
        }}
        replace
      />
    )
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/" replace />
  }

  return children
}

export default ProtectedRoute