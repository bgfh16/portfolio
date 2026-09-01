import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Users, MapPin, Plus } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import { useAuth } from '../context/AuthContext'
import './MyBookings.css'

function MyBookings() {
  const { user } = useAuth()

  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [cancellingId, setCancellingId] = useState(null)
  const [confirmingCancelId, setConfirmingCancelId] = useState(null)

  // tracks which booking's "add services" panel is currently open
  const [servicesOpenFor, setServicesOpenFor] = useState(null)
  // caches available services per hotel, so we don't refetch every toggle
  const [availableServices, setAvailableServices] = useState({})
  const [addingServiceId, setAddingServiceId] = useState(null)

  useEffect(() => {
    fetchBookings()
  }, [user])

  async function fetchBookings() {
    if (!user) return

    const { data, error } = await supabase
      .from('bookings')
      .select(`
        *,
        hotels ( name, city, country ),
        rooms ( room_type, image_url ),
        booking_services ( id, price_at_booking, services ( name ) )
      `)
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (error) console.error(error)

    // group active bookings first, cancelled ones last, keeping most
    // recent first within each group. for the cancelled group, "most
    // recent" means most recently cancelled, not most recently booked
    const sorted = [...(data || [])].sort((a, b) => {
      if (a.status === 'cancelled' && b.status !== 'cancelled') return 1
      if (a.status !== 'cancelled' && b.status === 'cancelled') return -1
      if (a.status === 'cancelled' && b.status === 'cancelled') {
        return new Date(b.cancelled_at) - new Date(a.cancelled_at)
      }
      return 0
    })

    setBookings(sorted)
    setLoading(false)
  }

  async function toggleServicesPanel(booking) {
    if (servicesOpenFor === booking.id) {
      setServicesOpenFor(null)
      return
    }

    setServicesOpenFor(booking.id)

    // only fetch this hotel's services if we haven't already cached them
    if (!availableServices[booking.hotel_id]) {
      const { data, error } = await supabase
        .from('services')
        .select('*')
        .eq('hotel_id', booking.hotel_id)

      if (error) {
        console.error(error)
        return
      }

      setAvailableServices((prev) => ({ ...prev, [booking.hotel_id]: data || [] }))
    }
  }

  // instead of inserting the service for free, this now creates a real
  // stripe checkout session for just this service's price, the actual
  // booking_services row only gets created once payment is confirmed,
  // on the payment success page, same pattern as the initial booking
  async function handleAddService(booking, service) {
    setAddingServiceId(service.id)

    const { data: sessionData, error: sessionError } = await supabase.functions.invoke(
      'create-checkout-session',
      {
        body: {
          type: 'service',
          description: `${service.name} — ${booking.hotels?.name}`,
          amount: service.price,
          successUrl: `${window.location.origin}/payment-success?booking_id=${booking.id}&service_id=${service.id}&service_price=${service.price}&session_id={CHECKOUT_SESSION_ID}`,
          cancelUrl: `${window.location.origin}/payment-cancelled?booking_id=${booking.id}`,
          metadata: { booking_id: booking.id, service_id: service.id, type: 'service' }
        }
      }
    )

    // only reset here on failure, since on success we are about to
    // navigate away entirely, resetting it here would briefly
    // re-enable the button right before the redirect actually happens
    if (sessionError || !sessionData?.url) {
      setAddingServiceId(null)
      console.error(sessionError)
      return
    }

    window.location.href = sessionData.url
  }

  async function handleCancel(bookingId) {
    setCancellingId(bookingId)

    const cancelledAt = new Date().toISOString()

    const { error } = await supabase
      .from('bookings')
      .update({ status: 'cancelled', cancelled_at: cancelledAt })
      .eq('id', bookingId)

    if (!error) {
      setBookings((prev) => {
        const updated = prev.map((b) =>
          b.id === bookingId ? { ...b, status: 'cancelled', cancelled_at: cancelledAt } : b
        )
        // re-sort so the just-cancelled booking correctly slots into
        // the cancelled group, ordered by cancellation recency
        return [...updated].sort((a, b) => {
          if (a.status === 'cancelled' && b.status !== 'cancelled') return 1
          if (a.status !== 'cancelled' && b.status === 'cancelled') return -1
          if (a.status === 'cancelled' && b.status === 'cancelled') {
            return new Date(b.cancelled_at) - new Date(a.cancelled_at)
          }
          return 0
        })
      })
      setConfirmingCancelId(null)
    }

    setCancellingId(null)
  }

  if (loading) {
    return <p className="my-bookings-status">Loading your bookings...</p>
  }

  return (
    <div className="my-bookings-page">
      <div className="my-bookings-header">
        <h1>My Bookings</h1>
        <p>View and manage your upcoming and past stays</p>
      </div>

      {bookings.length === 0 ? (
        <p className="my-bookings-empty">
          You don't have any bookings yet. <Link to="/hotels">Browse hotels</Link>
        </p>
      ) : (
        <div className="my-bookings-list">
          {bookings.map((booking) => {
            const servicesTotal = (booking.booking_services || []).reduce(
              (sum, bs) => sum + Number(bs.price_at_booking),
              0
            )
            const grandTotal = Number(booking.total_price) + servicesTotal

            return (
              <div key={booking.id} className={`my-booking-card ${booking.status === 'cancelled' ? 'is-cancelled' : ''}`}>
                <img
                  src={booking.rooms?.image_url}
                  alt={booking.rooms?.room_type}
                  className="my-booking-image"
                />

                <div className="my-booking-content">
                  <div className="my-booking-top">
                    <h3>{booking.rooms?.room_type}</h3>
                    <span className={`my-booking-status-tag ${booking.status}`}>
                      {booking.status === 'cancelled' ? 'Cancelled' : booking.status === 'pending' ? 'Pending' : 'Confirmed'}
                    </span>
                  </div>

                  <p className="my-booking-row">
                    <MapPin size={14} />
                    {booking.hotels?.name}, {booking.hotels?.city}, {booking.hotels?.country}
                  </p>

                  <p className="my-booking-row">
                    <Calendar size={14} />
                    {booking.check_in} — {booking.check_out}
                  </p>

                  <p className="my-booking-row">
                    <Users size={14} />
                    {booking.guests} guest{booking.guests > 1 ? 's' : ''}
                  </p>

                  <p className="my-booking-ref">Reference: {booking.reference_number}</p>
                  <p className="my-booking-total">Room total: ${booking.total_price}</p>

                  {booking.booking_services?.length > 0 && (
                    <div className="my-booking-services-list">
                      {booking.booking_services.map((bs) => (
                        <p key={bs.id} className="my-booking-service-item">
                          {bs.services?.name} — ${bs.price_at_booking}
                        </p>
                      ))}
                      <p className="my-booking-grand-total">Grand total: ${grandTotal}</p>
                    </div>
                  )}

                  {booking.status !== 'cancelled' && (
                    <>
                      <button
                        className="my-booking-services-toggle"
                        onClick={() => toggleServicesPanel(booking)}
                      >
                        <Plus size={14} /> Add Services
                      </button>

                      {servicesOpenFor === booking.id && (
                        <div className="my-booking-services-panel">
                          {(availableServices[booking.hotel_id] || []).length === 0 ? (
                            <p className="my-booking-services-empty">No services available for this hotel.</p>
                          ) : (
                            availableServices[booking.hotel_id].map((service) => {
                              const alreadyAdded = booking.booking_services?.some(
                                (bs) => bs.services?.name === service.name
                              )

                              return (
                                <div key={service.id} className="my-booking-service-option">
                                  <div>
                                    <p className="my-booking-service-name">{service.name}</p>
                                    <p className="my-booking-service-desc">{service.description}</p>
                                  </div>
                                  <div className="my-booking-service-right">
                                    <span>${service.price}</span>
                                    <button
                                      onClick={() => handleAddService(booking, service)}
                                      disabled={addingServiceId === service.id || alreadyAdded}
                                    >
                                      {alreadyAdded ? 'Added' : addingServiceId === service.id ? 'Redirecting...' : 'Pay & Add'}
                                    </button>
                                  </div>
                                </div>
                              )
                            })
                          )}
                        </div>
                      )}
                    </>
                  )}

                  {booking.status !== 'cancelled' && (
                    confirmingCancelId === booking.id ? (
                      <div className="my-booking-confirm">
                        <p>Cancel this booking?</p>
                        <div className="my-booking-confirm-buttons">
                          <button
                            className="my-booking-confirm-yes"
                            onClick={() => handleCancel(booking.id)}
                            disabled={cancellingId === booking.id}
                          >
                            {cancellingId === booking.id ? 'Cancelling...' : 'Yes, cancel'}
                          </button>
                          <button
                            className="my-booking-confirm-no"
                            onClick={() => setConfirmingCancelId(null)}
                          >
                            No, keep it
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        className="my-booking-cancel"
                        onClick={() => setConfirmingCancelId(booking.id)}
                      >
                        Cancel Booking
                      </button>
                    )
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <p className="my-bookings-policy">
        Free cancellation up to 48 hours before check-in. Cancellations within 48 hours of check-in may not be eligible for a refund.
      </p>
    </div>
  )
}

export default MyBookings