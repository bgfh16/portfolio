import { useState, useRef, useEffect } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Menu, X, ChevronDown } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import './Navbar.css'

function Navbar() {
  const navigate = useNavigate()
  const { user, isAdmin, loading, logout } = useAuth()

  const [menuOpen, setMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [confirmingLogout, setConfirmingLogout] = useState(false)
  const dropdownRef = useRef(null)

  const closeMenu = () => setMenuOpen(false)

  // this closes the dropdown if the user clicks anywhere outside of it
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
        setConfirmingLogout(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  async function handleLogout() {
    await logout()
    setDropdownOpen(false)
    setConfirmingLogout(false)
    closeMenu()
    navigate('/')
  }

  const firstName = user?.user_metadata?.full_name?.split(' ')[0] || 'Account'

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          <img
            src="https://txnlijkzhcmwrliivlzk.supabase.co/storage/v1/object/public/branding/logo-header2.png"
            alt="BookMyHotel"
            className="navbar-logo-img"
          />
        </Link>

        <button
          className="navbar-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X size={28} /> : <Menu size={28} />}
        </button>

        <div className={`navbar-links ${menuOpen ? 'navbar-links-open' : ''}`}>
          <NavLink to="/" end className="navbar-link" onClick={closeMenu}>Home</NavLink>
          <NavLink to="/hotels" className="navbar-link" onClick={closeMenu}>Hotels</NavLink>
          <NavLink to="/contact" className="navbar-link" onClick={closeMenu}>Contact</NavLink>

          {!loading && (
            user ? (
              <div className="navbar-user" ref={dropdownRef}>
                <button
                  className="navbar-user-btn"
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                >
                  {firstName}
                  <ChevronDown size={16} />
                </button>

                {dropdownOpen && (
                  <div className="navbar-dropdown">
                    {confirmingLogout ? (
                      <div className="navbar-dropdown-confirm">
                        <p>Are you sure you want to log out?</p>
                        <div className="navbar-dropdown-confirm-buttons">
                          <button
                            className="navbar-dropdown-confirm-yes"
                            onClick={handleLogout}
                          >
                            Yes, log out
                          </button>
                          <button
                            className="navbar-dropdown-confirm-no"
                            onClick={() => {
                              setConfirmingLogout(false)
                              setDropdownOpen(false)
                            }}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <Link
                          to="/my-bookings"
                          className="navbar-dropdown-item"
                          onClick={() => {
                            setDropdownOpen(false)
                            closeMenu()
                          }}
                        >
                          My Bookings
                        </Link>

                        {isAdmin && (
                          <>
                            <div className="navbar-dropdown-divider" />
                            <Link
                              to="/admin/hotels"
                              className="navbar-dropdown-item"
                              onClick={() => {
                                setDropdownOpen(false)
                                closeMenu()
                              }}
                            >
                              Manage Hotels
                            </Link>
                            <Link
                              to="/admin/reservations"
                              className="navbar-dropdown-item"
                              onClick={() => {
                                setDropdownOpen(false)
                                closeMenu()
                              }}
                            >
                              Manage Reservations
                            </Link>
                            <Link
                              to="/admin/promotions"
                              className="navbar-dropdown-item"
                              onClick={() => {
                                setDropdownOpen(false)
                                closeMenu()
                              }}
                            >
                              Manage Promotions
                            </Link>
                            <Link
                              to="/admin/services"
                              className="navbar-dropdown-item"
                              onClick={() => {
                                setDropdownOpen(false)
                                closeMenu()
                              }}
                            >
                              Manage Services
                            </Link>
                            <Link
                              to="/admin/messages"
                              className="navbar-dropdown-item"
                              onClick={() => {
                                setDropdownOpen(false)
                                closeMenu()
                              }}
                            >
                              View Messages
                            </Link>
                            <Link
                              to="/admin/analytics"
                              className="navbar-dropdown-item"
                              onClick={() => {
                                setDropdownOpen(false)
                                closeMenu()
                              }}
                            >
                              View Analytics
                            </Link>
                          </>
                        )}

                        <button
                          className="navbar-dropdown-item"
                          onClick={() => setConfirmingLogout(true)}
                        >
                          Logout
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <NavLink to="/login" className="navbar-link navbar-login-btn" onClick={closeMenu}>
                Login
              </NavLink>
            )
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar