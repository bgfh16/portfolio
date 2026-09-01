import { useState, useEffect } from 'react'
import { Star } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import { useAuth } from '../context/AuthContext'
import './ReviewSection.css'

function ReviewSection({ hotelId }) {
  const { user } = useAuth()

  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [canReview, setCanReview] = useState(false)

  const [rating, setRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    fetchReviews()
    if (user) checkEligibility()
  }, [hotelId, user])

  async function fetchReviews() {
    // joins public_profiles instead of the users table directly, since
    // public_profiles is a safe view exposing only id and full_name,
    // this keeps reviewer names visible to everyone without exposing
    // email or admin status
    const { data, error } = await supabase
      .from('reviews')
      .select('*, public_profiles ( full_name )')
      .eq('hotel_id', hotelId)
      .order('created_at', { ascending: false })

    if (error) console.error(error)
    setReviews(data || [])
    setLoading(false)
  }

  // checks if this user has a booking for this hotel, which is the
  // same condition the database itself enforces, we check it here too
  // so we can show or hide the review form before they even try
  async function checkEligibility() {
    const { data } = await supabase
      .from('bookings')
      .select('id')
      .eq('user_id', user.id)
      .eq('hotel_id', hotelId)
      .limit(1)

    setCanReview((data || []).length > 0)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (rating === 0) {
      setError('Please select a star rating')
      return
    }

    setSubmitting(true)

    const { error } = await supabase.from('reviews').insert({
      user_id: user.id,
      hotel_id: hotelId,
      rating,
      comment
    })

    setSubmitting(false)

    if (error) {
      setError('Something went wrong submitting your review. Please try again.')
      return
    }

    setSubmitted(true)
    setRating(0)
    setComment('')
    fetchReviews()
    setTimeout(() => setSubmitted(false), 4000)
  }

  const averageRating = reviews.length > 0
    ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
    : null

  if (loading) {
    return <p className="review-status">Loading reviews...</p>
  }

  return (
    <section className="review-section">
      <div className="review-header">
        <h2>Guest Reviews</h2>
        {averageRating && (
          <div className="review-average">
            <Star size={18} fill="#3D5A80" color="#3D5A80" />
            <span>{averageRating} out of 5</span>
            <span className="review-count">({reviews.length} review{reviews.length > 1 ? 's' : ''})</span>
          </div>
        )}
      </div>

      {canReview && !submitted && (
        <form onSubmit={handleSubmit} className="review-form">
          <p className="review-form-label">Leave a review</p>

          <div className="review-star-input">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                type="button"
                key={star}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                aria-label={`Rate ${star} stars`}
              >
                <Star
                  size={26}
                  fill={star <= (hoverRating || rating) ? '#3D5A80' : 'none'}
                  color="#3D5A80"
                />
              </button>
            ))}
          </div>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Share your experience..."
            rows={3}
            required
          />

          {error && <p className="review-error">{error}</p>}

          <button type="submit" className="review-submit" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit Review'}
          </button>
        </form>
      )}

      {submitted && (
        <p className="review-thank-you">Thank you for your review!</p>
      )}

      {reviews.length === 0 ? (
        <p className="review-empty">No reviews yet for this hotel.</p>
      ) : (
        <div className="review-list">
          {reviews.map((review) => (
            <div key={review.id} className="review-item">
              <div className="review-item-top">
                <span className="review-item-name">{review.public_profiles?.full_name || 'Guest'}</span>
                <span className="review-item-stars">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      size={14}
                      fill={i < review.rating ? '#3D5A80' : 'none'}
                      color="#3D5A80"
                    />
                  ))}
                </span>
              </div>
              <p className="review-item-comment">{review.comment}</p>
              <p className="review-item-date">
                {new Date(review.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

export default ReviewSection