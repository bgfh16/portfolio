import { useState, useEffect } from 'react'
import { Calendar, Users, MapPin } from 'lucide-react'
import { supabase } from '../../utils/supabaseClient'
import './AdminReservations.css'

function AdminReservations() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)

  const [cancellingId, setCancellingId] = useState(null)
  const [confirmingCancelId, setConfirmingCancelId] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')

  const [dateFilter, setDateFilter] = useState('')
  const [refSearch, setRefSearch] = useState('')

  useEffect(() => {
    fetchBookings()
  }, [])

  async function fetchBookings() {
    // pulls every booking across every guest, along with the hotel,
    // room, and guest name/email so admins have full context in one view
    const { data, error } = await supabase
      .from('bookings')
      .select(`
        *,
        hotels ( name, city, country ),
        rooms ( room_type ),
        users ( full_name, email )
      `)
      .order('created_at', { ascending: false })

    if (error) console.error(error)
    setBookings(data || [])
    setLoading(false)
  }

  async function handleCancel(bookingId) {
    setCancellingId(bookingId)

    const { error } = await supabase
      .from('bookings')
      .update({ status: 'cancelled', cancelled_at: new Date().toISOString() })
      .eq('id', bookingId)

    if (!error) {
      setBookings((prev) =>
        prev.map((b) => (b.id === bookingId ? { ...b, status: 'cancelled' } : b))
      )
      setConfirmingCancelId(null)
      setSuccessMessage('Booking cancelled successfully.')
      window.scrollTo({ top: 0, behavior: 'smooth' })
      setTimeout(() => setSuccessMessage(''), 3000)
    }

    setCancellingId(null)
  }

  const filteredBookings = bookings.filter((b) => {
    const matchesDate = !dateFilter || (b.check_in <= dateFilter && b.check_out >= dateFilter)
    const matchesRef = !refSearch || b.reference_number?.toLowerCase().includes(refSearch.toLowerCase())
    return matchesDate && matchesRef
  })

  if (loading) {
    return <p className="admin-res-status">Loading reservations...</p>
  }

  return (
    <div className="admin-res-page">
      {successMessage && <p className="admin-success-message">{successMessage}</p>}

      <div className="admin-res-header">
        <div>
          <h1>Manage Reservations</h1>
          <p>View and manage all guest bookings across every hotel</p>
        </div>
        <div className="admin-res-filter">
          <label>
            Search reference
            <input
              type="text"
              placeholder="e.g. A3F9K2XZ"
              value={refSearch}
              onChange={(e) => setRefSearch(e.target.value)}
            />
          </label>
          <label>
            Filter by date
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
          </label>
          {(dateFilter || refSearch) && (
            <button
              onClick={() => { setDateFilter(''); setRefSearch('') }}
              className="admin-res-clear-filter"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="admin-res-table">
        <div className="admin-res-row admin-res-row-head">
          <span>Reference</span>
          <span>Guest</span>
          <span>Hotel</span>
          <span>Room</span>
          <span>Dates</span>
          <span>Booked On</span>
          <span>Status</span>
          <span>Actions</span>
        </div>

        {filteredBookings.map((booking) => (
          <div key={booking.id} className="admin-res-row">
            <span className="admin-res-ref">{booking.reference_number}</span>
            <span>
              <span className="admin-res-guest-name">{booking.users?.full_name}</span>
              <span className="admin-res-guest-email">{booking.users?.email}</span>
            </span>

            <span>
              <MapPin size={13} />
              {booking.hotels?.name}
            </span>

            <span>{booking.rooms?.room_type}</span>

            <span>
              <Calendar size={13} />
              {booking.check_in} to {booking.check_out}
            </span>

            <span className="admin-res-booked-on">
              {new Date(booking.created_at).toLocaleDateString()}
            </span>

            <span className={`admin-res-status-tag ${booking.status}`}>
              {booking.status === 'cancelled' ? 'Cancelled' : booking.status === 'pending' ? 'Pending' : 'Confirmed'}
            </span>

            <span className="admin-res-actions">
              {booking.status === 'cancelled' ? (
                <span className="admin-res-cancelled-label">Cancelled</span>
              ) : (
                confirmingCancelId === booking.id ? (
                  <span className="admin-res-confirm">
                    <button
                      onClick={() => handleCancel(booking.id)}
                      disabled={cancellingId === booking.id}
                      className="admin-res-confirm-yes"
                    >
                      {cancellingId === booking.id ? 'Cancelling...' : 'Confirm'}
                    </button>
                    <button
                      onClick={() => setConfirmingCancelId(null)}
                      className="admin-res-confirm-no"
                    >
                      Cancel
                    </button>
                  </span>
                ) : (
                  <button
                    onClick={() => setConfirmingCancelId(booking.id)}
                    className="admin-res-cancel-btn"
                  >
                    Cancel Booking
                  </button>
                )
              )}
            </span>
          </div>
        ))}
        {filteredBookings.length === 0 && (
          <p className="admin-res-no-results">No reservations found for this date.</p>
        )}
      </div>
    </div>
  )
}

export default AdminReservations