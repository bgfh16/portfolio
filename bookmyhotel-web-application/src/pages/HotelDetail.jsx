import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { MapPin, Star, Leaf, ArrowLeft, Sparkles } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import ReviewSection from '../components/ReviewSection'
import './HotelDetail.css'

// this page shows the full details for one specific hotel
// it reads the hotel's id from the url, then fetches just that one row 
function HotelDetail() {
// useParams reads the dynamic part of the url we set up in App.jsx (:id)
  const { id } = useParams()
  const navigate = useNavigate()

  const [hotel, setHotel] = useState(null)
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchHotel() {
      const { data, error } = await supabase
        .from('hotels')
        .select('*')
        .eq('id', id)
        .single()

      if (error) {
        console.error('Error fetching hotel:', error)
      } else {
        setHotel(data)
      }

      setLoading(false)
    }

    fetchHotel()
  }, [id])

  useEffect(() => {
    async function fetchServices() {
      // pulls the paid additional services offered at this specific
      // hotel, shown here just for information, guests actually add
      // them to a booking from the booking form or my bookings page
      const { data, error } = await supabase
        .from('services')
        .select('*')
        .eq('hotel_id', id)

      if (error) {
        console.error('Error fetching services:', error)
      } else {
        setServices(data || [])
      }
    }

    fetchServices()
  }, [id])

  if (loading) {
    return <p className="detail-status">Loading hotel...</p>
  }

  if (!hotel) {
    return <p className="detail-status">Hotel not found.</p>
  }

  return (
    <div className="hotel-detail">

      {/* hero banner using the hotel's cover image */}
      <section
        className="detail-hero"
        style={{ backgroundImage: `url(${hotel.image_url})` }}
      >
        <div className="detail-hero-overlay">
          <button onClick={() => navigate(-1)} className="detail-back-link">
            <ArrowLeft size={16} />
            Back
          </button>

          <h1>{hotel.name}</h1>
          <p className="detail-location">
            <MapPin size={16} />
            {hotel.city}, {hotel.country}
          </p>
        </div>
      </section>

      {/* main info section */}
      <section className="detail-content">
        <div className="detail-main">
          <div className="detail-rating">
            {Array.from({ length: hotel.star_rating }).map((_, index) => (
              <Star key={index} size={18} fill="var(--color-primary)" color="var(--color-primary)" />
            ))}
            <span>{hotel.star_rating}-Star Hotel</span>
          </div>

          <h2>About This Hotel</h2>
          <p className="detail-description">{hotel.description}</p>

          <h2>Facilities</h2>
          <div className="facility-tags">
            {hotel.facilities?.map((facility) => (
              <span key={facility} className="facility-tag">{facility}</span>
            ))}
          </div>

          {services.length > 0 && (
            <>
              <h2>Available Services</h2>
              <p className="detail-services-note">
                These paid extras can be added when you book, or anytime afterward from My Bookings.
              </p>
              <div className="detail-services-list">
                {services.map((service) => (
                  <div key={service.id} className="detail-service-item">
                    <div className="detail-service-icon">
                      <Sparkles size={18} />
                    </div>
                    <div className="detail-service-info">
                      <p className="detail-service-name">{service.name}</p>
                      {service.description && (
                        <p className="detail-service-desc">{service.description}</p>
                      )}
                    </div>
                    <p className="detail-service-price">${service.price}</p>
                  </div>
                ))}
              </div>
            </>
          )}

          <div className="sustainability-box">
            <Leaf size={20} />
            <div>
              <h3>Sustainability</h3>
              <p>{hotel.sustainability_info}</p>
            </div>
          </div>
        </div>

        {/* sidebar with price and a placeholder for booking, until rooms exist */}
        <div className="detail-sidebar">
          <p className="sidebar-price-label">Starting from</p>
          <p className="sidebar-price">${hotel.price_from} <span>/ night</span></p>
          <button className="sidebar-button" onClick={() => navigate(`/hotels/${hotel.id}/rooms`)}>
            View Rooms
          </button>
        </div>
      </section>

      <ReviewSection hotelId={hotel.id} />

    </div>
  )
}

export default HotelDetail