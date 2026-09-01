import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { CheckCircle2, Loader2 } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import './PaymentSuccess.css'

function PaymentSuccess() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const bookingId = searchParams.get('booking_id')
  const sessionId = searchParams.get('session_id')
  const serviceId = searchParams.get('service_id')
  const servicePrice = searchParams.get('service_price')

  const [status, setStatus] = useState('verifying') // verifying, success, failed
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    async function verifyAndConfirm() {
      if (!bookingId || !sessionId) {
        setStatus('failed')
        setErrorMessage('Missing payment details.')
        return
      }

      // ask our edge function to confirm with stripe that this specific
      // session actually completed successfully, rather than trusting
      // the redirect alone, since a url can be typed or revisited freely
      const { data, error } = await supabase.functions.invoke('verify-payment', {
        body: { sessionId }
      })

      if (error || !data?.paid) {
        setStatus('failed')
        setErrorMessage('We could not verify your payment. Please contact support if you were charged.')
        return
      }

      if (serviceId) {
        // attempt the insert directly, relying on the database's unique
        // constraint on stripe_session_id to reject a duplicate outright,
        // this is safe against race conditions in a way a check-then-insert
        // pattern is not, since the database guarantees atomicity
        const { error: serviceInsertError } = await supabase
          .from('booking_services')
          .insert({
            booking_id: bookingId,
            service_id: serviceId,
            price_at_booking: servicePrice,
            stripe_session_id: sessionId
          })

        // error code 23505 means a unique constraint violation, meaning
        // this exact session was already processed, which is expected and
        // fine, not a real failure, so we don't show an error for it
        if (serviceInsertError && serviceInsertError.code !== '23505') {
          setStatus('failed')
          setErrorMessage('Payment succeeded but we could not add the service to your booking. Please contact support.')
          return
        }
      } else {
        // payment genuinely confirmed, now update the booking's status
        const { error: updateError } = await supabase
          .from('bookings')
          .update({ status: 'confirmed' })
          .eq('id', bookingId)

        if (updateError) {
          setStatus('failed')
          setErrorMessage('Payment succeeded but we could not update your booking. Please contact support.')
          return
        }
      }

      setStatus('success')

      // send them on to the my bookings page after a short pause,
      // since this page's only job was to verify and confirm
      setTimeout(() => {
        navigate('/my-bookings')
      }, 3000)
    }

    verifyAndConfirm()
  }, [bookingId, sessionId, serviceId, servicePrice, navigate])

  return (
    <div className="payment-status-page">
      <div className="payment-status-card">
        {status === 'verifying' && (
          <>
            <div className="payment-status-icon verifying">
              <Loader2 size={48} strokeWidth={1.5} className="spin" />
            </div>
            <h1>Confirming Your Payment</h1>
            <p>Please wait a moment while we confirm your booking.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="payment-status-icon success">
              <CheckCircle2 size={48} strokeWidth={1.5} />
            </div>
            <h1>Payment Successful</h1>
            <p>Your booking is confirmed. Redirecting you to My Bookings...</p>
          </>
        )}

        {status === 'failed' && (
          <>
            <div className="payment-status-icon failed">
              <CheckCircle2 size={48} strokeWidth={1.5} />
            </div>
            <h1>Something Went Wrong</h1>
            <p>{errorMessage}</p>
            <Link to="/my-bookings" className="payment-status-link">
              Go to My Bookings
            </Link>
          </>
        )}
      </div>
    </div>
  )
}

export default PaymentSuccess