import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../utils/supabaseClient'

// this context holds the current logged in user (or null if logged out)
// so any component in the app can check auth state without repeating
// the supabase session logic every time
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // user holds the supabase auth user object, or null if not logged in
  const [user, setUser] = useState(null)

  // isAdmin holds whether the current user has admin access, checked
  // against the is_admin column on the users table, defaults to false
  const [isAdmin, setIsAdmin] = useState(false)

  // loading is true while we are still checking if there is an existing
  // session, this stops the navbar flashing "login" then "logged in"
  // for a split second on page refresh
  const [loading, setLoading] = useState(true)

  // this checks the users table for the is_admin flag on the given
  // user id, and updates our isAdmin state accordingly
  async function checkAdminStatus(userId) {
    if (!userId) {
      setIsAdmin(false)
      return
    }

    const { data, error } = await supabase
      .from('users')
      .select('is_admin')
      .eq('id', userId)
      .single()

    if (error) {
      setIsAdmin(false)
      return
    }

    setIsAdmin(data?.is_admin || false)
  }

  useEffect(() => {
    // on first load, check if there is already a logged in session
    // this handles the case where someone refreshes the page while
    // still logged in, supabase keeps the session in local storage
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setUser(session?.user ?? null)
      await checkAdminStatus(session?.user?.id)
      setLoading(false)
    })

    // this listens for auth changes going forward, login, logout,
    // token refresh, etc, and keeps our user state in sync automatically
    const { data: listener } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setUser(session?.user ?? null)
      await checkAdminStatus(session?.user?.id)
    })

    // cleanup, stop listening when this provider unmounts
    return () => {
      listener.subscription.unsubscribe()
    }
  }, [])

  // logout function, any component can call this via useAuth()
  async function logout() {
    await supabase.auth.signOut()
  }

  return (
    <AuthContext.Provider value={{ user, isAdmin, loading, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// custom hook so components can just call useAuth() instead of
// importing useContext and AuthContext separately every time
export function useAuth() {
  return useContext(AuthContext)
}