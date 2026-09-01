import { useLocation, useNavigate, Link } from 'react-router-dom'
import { CheckCircle2, Calendar, Users, MapPin } from 'lucide-react'
import './BookingConfirmation.css'

function BookingConfirmation() {
  const location = useLocation()
  const navigate = useNavigate()

  const { booking, hotel, room } = location.state || {}

  if (!booking || !hotel || !room) {
    navigate('/')
    return null
  }

  const nights = Math.round(
    (new Date(booking.check_out) - new Date(booking.check_in)) / (1000 * 60 * 60 * 24)
  )

  return (
    <div className="booking-confirmation-page">
      <div className="booking-confirmation-card">
        <img
          src={room.image_url}
          alt={room.room_type}
          className="booking-confirmation-image"
        />

        <div className="booking-confirmation-body">
          <div className="booking-confirmation-icon">
            <CheckCircle2 size={40} strokeWidth={1.5} />
          </div>

          <h1>Booking Confirmed</h1>
          <p className="booking-confirmation-subtitle">
            Your stay at {hotel.name} is booked. A confirmation has been saved
            to your account.
          </p>

          <div className="booking-confirmation-details">
            <div className="booking-confirmation-row">
              <MapPin size={16} />
              <span>
                {hotel.name}, {hotel.city}, {hotel.country}
              </span>
            </div>

            <div className="booking-confirmation-row">
              <Calendar size={16} />
              <span>
                {booking.check_in} — {booking.check_out} ({nights} night
                {nights > 1 ? "s" : ""})
              </span>
            </div>

            <div className="booking-confirmation-row">
              <Users size={16} />
              <span>
                {booking.guests} guest{booking.guests > 1 ? "s" : ""}
              </span>
            </div>

            <div className="booking-confirmation-room">
              <p className="booking-confirmation-room-type">{room.room_type}</p>
              <p className="booking-confirmation-total">
                Total Paid: ${booking.total_price}
              </p>
              <p className="booking-confirmation-ref">
                Booking Reference: {booking.reference_number}
              </p>
            </div>
          </div>

          <div className="booking-confirmation-actions">
            <Link to="/" className="booking-confirmation-home">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BookingConfirmation