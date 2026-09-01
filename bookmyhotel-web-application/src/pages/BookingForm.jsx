import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Users, Calendar, Tag, Sparkles } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import { useAuth } from '../context/AuthContext'
import './BookingForm.css'

function BookingForm() {
  const { id, roomId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [hotel, setHotel] = useState(null)
  const [room, setRoom] = useState(null)
  const [bookedRanges, setBookedRanges] = useState([])
  const [availableServices, setAvailableServices] = useState([])
  const [selectedServiceIds, setSelectedServiceIds] = useState([])
  const [loading, setLoading] = useState(true)

  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [guests, setGuests] = useState(1)

  const [promoCode, setPromoCode] = useState('')
  const [appliedPromo, setAppliedPromo] = useState(null)
  const [promoError, setPromoError] = useState('')
  const [checkingPromo, setCheckingPromo] = useState(false)
  const [availablePromos, setAvailablePromos] = useState([])

  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const today = new Date().toISOString().split('T')[0]

  useEffect(() => {
    async function fetchData() {
      const hotelResult = await supabase.from('hotels').select('*').eq('id', id).single()
      const roomResult = await supabase.from('rooms').select('*').eq('id', roomId).single()

      const bookingsResult = await supabase
        .from('bookings')
        .select('check_in, check_out')
        .eq('room_id', roomId)
        .eq('status', 'confirmed')

      const servicesResult = await supabase
        .from('services')
        .select('*')
        .eq('hotel_id', id)

      if (hotelResult.error) console.error(hotelResult.error)
      if (roomResult.error) console.error(roomResult.error)
      if (bookingsResult.error) console.error(bookingsResult.error)
      if (servicesResult.error) console.error(servicesResult.error)

      setHotel(hotelResult.data)
      setRoom(roomResult.data)
      setBookedRanges(bookingsResult.data || [])
      setAvailableServices(servicesResult.data || [])
      setLoading(false)
    }

    fetchData()
  }, [id, roomId])

  useEffect(() => {
    async function fetchAvailablePromos() {
      const { data, error } = await supabase
        .from('promotions')
        .select('code, discount_percent, expires_at')
        .eq('is_active', true)
        .or(`expires_at.is.null,expires_at.gte.${today}`)

      if (error) {
        console.error(error)
        return
      }

      setAvailablePromos(data || [])
    }

    fetchAvailablePromos()
  }, [today])

  function getNights() {
    if (!checkIn || !checkOut) return 0
    const start = new Date(checkIn)
    const end = new Date(checkOut)
    const diff = (end - start) / (1000 * 60 * 60 * 24)
    return diff > 0 ? diff : 0
  }

  function toggleService(serviceId) {
    setSelectedServiceIds((prev) =>
      prev.includes(serviceId)
        ? prev.filter((sid) => sid !== serviceId)
        : [...prev, serviceId]
    )
  }

  const nights = getNights()
  const roomSubtotal = room ? nights * room.price_per_night : 0
  const discountAmount = appliedPromo
    ? Math.round((roomSubtotal * appliedPromo.discount_percent) / 100)
    : 0
  const roomTotal = roomSubtotal - discountAmount

  const selectedServices = availableServices.filter((s) => selectedServiceIds.includes(s.id))
  const servicesTotal = selectedServices.reduce((sum, s) => sum + Number(s.price), 0)

  const grandTotal = roomTotal + servicesTotal

  function datesOverlapExisting(inDate, outDate) {
    if (!inDate || !outDate) return false
    return bookedRanges.some((b) => inDate < b.check_out && outDate > b.check_in)
  }

  const hasConflict = datesOverlapExisting(checkIn, checkOut)

  async function handleApplyPromo() {
    setPromoError('')
    setCheckingPromo(true)

    const cleanCode = promoCode.trim().toUpperCase()

    const { data, error } = await supabase
      .from('promotions')
      .select('*')
      .eq('code', cleanCode)
      .eq('is_active', true)
      .maybeSingle()

    setCheckingPromo(false)

    if (error || !data) {
      setPromoError('This promo code is invalid or no longer active.')
      setAppliedPromo(null)
      return
    }

    if (data.expires_at && data.expires_at < today) {
      setPromoError('This promo code has expired.')
      setAppliedPromo(null)
      return
    }

    setAppliedPromo(data)
  }

  function handleRemovePromo() {
    setAppliedPromo(null)
    setPromoCode('')
    setPromoError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!checkIn || !checkOut) {
      setError('Please select both check-in and check-out dates')
      return
    }

    if (nights <= 0) {
      setError('Check-out date must be after check-in date')
      return
    }

    if (guests > room.capacity) {
      setError(`This room fits up to ${room.capacity} guests`)
      return
    }

    if (hasConflict) {
      setError('This room is already booked for part of your selected dates. Please choose different dates.')
      return
    }

    setSubmitting(true)

    const { data: overlapping, error: overlapError } = await supabase
      .from('bookings')
      .select('id')
      .eq('room_id', roomId)
      .eq('status', 'confirmed')
      .lt('check_in', checkOut)
      .gt('check_out', checkIn)

    if (overlapError) {
      setSubmitting(false)
      setError('Something went wrong checking availability. Please try again.')
      return
    }

    if (overlapping.length > 0) {
      setSubmitting(false)
      setError('This room is already booked for part of your selected dates. Please choose different dates.')
      return
    }

    // create the booking as pending first, it only becomes confirmed
    // once stripe confirms the payment actually succeeded
    const { data: newBooking, error: insertError } = await supabase
      .from('bookings')
      .insert({
        user_id: user.id,
        room_id: roomId,
        hotel_id: id,
        check_in: checkIn,
        check_out: checkOut,
        guests,
        total_price: roomTotal,
        status: 'pending',
        promotion_id: appliedPromo?.id || null
      })
      .select()
      .single()

    if (insertError) {
      setSubmitting(false)
      setError('Something went wrong creating your booking. Please try again.')
      return
    }

    // attach any selected services to this booking now, before payment,
    // storing today's price so future price changes do not affect this
    // booking retroactively
    if (selectedServices.length > 0) {
      const serviceRows = selectedServices.map((s) => ({
        booking_id: newBooking.id,
        service_id: s.id,
        price_at_booking: s.price
      }))

      const { error: servicesInsertError } = await supabase
        .from('booking_services')
        .insert(serviceRows)

      if (servicesInsertError) {
        setSubmitting(false)
        setError('Something went wrong adding your selected services. Please try again.')
        return
      }
    }

    // now create a stripe checkout session for the full total,
    // room plus any selected services combined into one payment
    const { data: sessionData, error: sessionError } = await supabase.functions.invoke(
      'create-checkout-session',
      {
        body: {
          type: 'booking',
          description: `${room.room_type} at ${hotel.name}`,
          amount: grandTotal,
          successUrl: `${window.location.origin}/payment-success?booking_id=${newBooking.id}&session_id={CHECKOUT_SESSION_ID}`,
          cancelUrl: `${window.location.origin}/payment-cancelled?booking_id=${newBooking.id}`,
          metadata: { booking_id: newBooking.id, type: 'booking' }
        }
      }
    )

    // only reset submitting on failure, since on success we are about
    // to navigate away entirely, resetting it here would briefly
    // re-enable the button right before the redirect actually happens
    if (sessionError || !sessionData?.url) {
      setSubmitting(false)
      setError('Something went wrong starting payment. Please try again.')
      return
    }

    window.location.href = sessionData.url
  }

  if (loading) {
    return <p className="booking-form-status">Loading...</p>
  }

  if (!hotel || !room) {
    return <p className="booking-form-status">Room not found.</p>
  }

  return (
    <div className="booking-form-page">
      <div className="booking-form-card">
        <button onClick={() => navigate(-1)} className="booking-form-back">
          <ArrowLeft size={16} />
          Back
        </button>

        <h1>Book Your Stay</h1>
        <div className="booking-form-room-preview">
          <img src={room.image_url} alt={room.room_type} className="booking-form-room-thumb" />
          <p className="booking-form-subtitle">{room.room_type} at {hotel.name}</p>
        </div>

        {bookedRanges.length > 0 && (
          <div className="booking-form-unavailable">
            <p>Already booked:</p>
            <ul>
              {bookedRanges.map((b, i) => (
                <li key={i}>{b.check_in} to {b.check_out}</li>
              ))}
            </ul>
          </div>
        )}

        <form onSubmit={handleSubmit} className="booking-form">
          <div className="booking-form-row">
            <label>
              <Calendar size={14} /> Check-In
              <input
                type="date"
                value={checkIn}
                min={today}
                onChange={(e) => setCheckIn(e.target.value)}
                required
              />
            </label>

            <label>
              <Calendar size={14} /> Check-Out
              <input
                type="date"
                value={checkOut}
                min={checkIn || today}
                onChange={(e) => setCheckOut(e.target.value)}
                required
              />
            </label>
          </div>

          <label>
            <Users size={14} /> Guests
            <input
              type="number"
              value={guests}
              min={1}
              max={room.capacity}
              onChange={(e) => {
                const value = Number(e.target.value)
                if (value < 1) {
                  setGuests(1)
                } else if (value > room.capacity) {
                  setGuests(room.capacity)
                } else {
                  setGuests(value)
                }
              }}
              required
            />
          </label>

          {availableServices.length > 0 && (
            <div className="booking-form-services">
              <label>
                <Sparkles size={14} /> Add Services (optional)
              </label>
              <div className="booking-form-services-list">
                {availableServices.map((service) => (
                  <label key={service.id} className="booking-form-service-option">
                    <input
                      type="checkbox"
                      checked={selectedServiceIds.includes(service.id)}
                      onChange={() => toggleService(service.id)}
                    />
                    <div className="booking-form-service-text">
                      <span className="booking-form-service-name">{service.name}</span>
                      {service.description && (
                        <span className="booking-form-service-desc">{service.description}</span>
                      )}
                    </div>
                    <span className="booking-form-service-price">${service.price}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="booking-form-promo">
            <label>
              <Tag size={14} /> Promo Code (optional)
            </label>

            {availablePromos.length > 0 && !appliedPromo && (
              <div className="booking-form-promo-hints">
                {availablePromos.map((promo) => (
                  <button
                    key={promo.code}
                    type="button"
                    className="booking-form-promo-hint-chip"
                    onClick={() => setPromoCode(promo.code)}
                  >
                    {promo.code} — {promo.discount_percent}% off
                  </button>
                ))}
              </div>
            )}

            {appliedPromo ? (
              <div className="booking-form-promo-applied">
                <span>
                  <strong>{appliedPromo.code}</strong> applied — {appliedPromo.discount_percent}% off
                </span>
                <button type="button" onClick={handleRemovePromo}>
                  Remove
                </button>
              </div>
            ) : (
              <div className="booking-form-promo-input">
                <input
                  type="text"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value)}
                  placeholder="Enter code"
                />
                <button
                  type="button"
                  onClick={handleApplyPromo}
                  disabled={checkingPromo || !promoCode.trim()}
                >
                  {checkingPromo ? 'Checking...' : 'Apply'}
                </button>
              </div>
            )}

            {promoError && <p className="booking-form-promo-error">{promoError}</p>}
          </div>

          {hasConflict && (
            <p className="booking-form-conflict">
              These dates overlap with an existing booking. Please choose different dates.
            </p>
          )}

          {nights > 0 && !hasConflict && (
            <div className="booking-form-summary">
              <p>${room.price_per_night} x {nights} night{nights > 1 ? 's' : ''}</p>
              <p className="booking-form-subtotal">Room subtotal: ${roomSubtotal}</p>
              {appliedPromo && (
                <p className="booking-form-discount">
                  Discount ({appliedPromo.discount_percent}%): -${discountAmount}
                </p>
              )}
              {selectedServices.length > 0 && (
                <>
                  {selectedServices.map((s) => (
                    <p key={s.id} className="booking-form-service-line">
                      {s.name}: ${s.price}
                    </p>
                  ))}
                </>
              )}
              <p className="booking-form-total">Total: ${grandTotal}</p>
            </div>
          )}

          {error && <p className="booking-form-error">{error}</p>}

          <button type="submit" className="booking-form-button" disabled={submitting || hasConflict}>
            {submitting ? 'Redirecting to payment...' : 'Confirm Booking'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default BookingForm