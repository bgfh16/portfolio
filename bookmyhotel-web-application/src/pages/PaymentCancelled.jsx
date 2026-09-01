import { useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { XCircle } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import './PaymentSuccess.css'

function PaymentCancelled() {
  const [searchParams] = useSearchParams()
  const bookingId = searchParams.get('booking_id')

  useEffect(() => {
    // if payment was cancelled, clean up the pending booking we created
    // so it doesn't sit around looking like a real reservation
    async function cancelPendingBooking() {
      if (bookingId) {
        await supabase.from('bookings').update({ status: 'cancelled' }).eq('id', bookingId)
      }
    }

    cancelPendingBooking()
  }, [bookingId])

  return (
    <div className="payment-status-page">
      <div className="payment-status-card">
        <div className="payment-status-icon failed">
          <XCircle size={48} strokeWidth={1.5} />
        </div>
        <h1>Payment Cancelled</h1>
        <p>Your payment was not completed, and no charge was made. You can try booking again anytime.</p>
        <Link to="/hotels" className="payment-status-link">
          Browse Hotels
        </Link>
      </div>
    </div>
  )
}

export default PaymentCancelled