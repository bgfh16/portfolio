import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Search, MapPin, Leaf, ShieldCheck, Star } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import HotelCard from '../components/HotelCard'
import './Home.css'

// this is our landing page, it has the hero section with a search bar
// then a row of usps (unique selling points) and a hotel showcase section
function Home() {
  const navigate = useNavigate()

  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(true)
  const [reviews, setReviews] = useState([])
  const [searchInput, setSearchInput] = useState('')

  useEffect(() => {
    async function fetchHotels() {
      const { data, error } = await supabase
        .from('hotels')
        .select('*')
        .limit(4)

      if (error) {
        console.error('Error fetching hotels:', error)
      } else {
        setHotels(data)
      }

      setLoading(false)
    }

    fetchHotels()
  }, [])

  useEffect(() => {
    async function fetchReviews() {
      // pull a handful of the most recent 4 and 5 star reviews across
      // every hotel, joining public_profiles instead of the users table
      // directly, since public_profiles is a safe view exposing only
      // id and full_name, keeping email and admin status protected
      const { data, error } = await supabase
        .from('reviews')
        .select('*, hotels ( name ), public_profiles ( full_name )')
        .gte('rating', 4)
        .order('created_at', { ascending: false })
        .limit(3)

      if (error) {
        console.error('Error fetching reviews:', error)
      } else {
        setReviews(data || [])
      }
    }

    fetchReviews()
  }, [])

  function handleSearch(e) {
    e.preventDefault()
    if (searchInput.trim()) {
      navigate(`/hotels?search=${encodeURIComponent(searchInput.trim())}`)
    } else {
      navigate('/hotels')
    }
  }

  return (
    <div className="home">

      <section className="hero">
        <div className="hero-overlay">
          <h1 className="hero-title">Five-Star Stays Across Our Global Collection</h1>
          <p className="hero-subtitle">
            Where comfort meets elegance, wherever you travel
          </p>

          <form className="search-bar" onSubmit={handleSearch}>
            <div className="search-field">
              <MapPin size={18} />
              <input
                type="text"
                placeholder="Where are you going?"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
            </div>
            <button type="submit" className="search-button">
              <Search size={18} />
              Search
            </button>
          </form>
        </div>
      </section>

      <section className="usps">
        <div className="usp-item">
          <Star size={28} />
          <h3>Five Star Properties</h3>
          <p>Curated luxury hotels across Asia and Europe</p>
        </div>
        <div className="usp-item">
          <Leaf size={28} />
          <h3>Sustainability First</h3>
          <p>Every hotel meets our eco friendly standards</p>
        </div>
        <div className="usp-item">
          <ShieldCheck size={28} />
          <h3>Secure Booking</h3>
          <p>Your payments and data are always protected</p>
        </div>
      </section>

      <section className="showcase">
        <h2>Featured Hotels</h2>
        <p>A glimpse of our five-star collection</p>

        {loading ? (
          <p className="showcase-loading">Loading hotels...</p>
        ) : (
          <div className="hotel-grid">
            {hotels.map((hotel) => (
              <HotelCard key={hotel.id} hotel={hotel} />
            ))}
          </div>
        )}

        <Link to="/hotels" className="showcase-view-all">
          View All Hotels
        </Link>
      </section>

      {reviews.length > 0 && (
        <section className="testimonials">
          <h2>What Our Guests Say</h2>
          <div className="testimonial-grid">
            {reviews.map((review) => (
              <div key={review.id} className="testimonial-card">
                <div className="testimonial-stars">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      size={14}
                      fill={i < review.rating ? '#3D5A80' : 'none'}
                      color="#3D5A80"
                    />
                  ))}
                </div>
                <p className="testimonial-comment">"{review.comment}"</p>
                <p className="testimonial-meta">
                  {review.public_profiles?.full_name || 'Guest'} · {review.hotels?.name}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="cta-band">
        <h2>Ready for Your Next Stay?</h2>
        <p>Explore our full collection of five-star hotels and start planning your escape.</p>
        <Link to="/hotels" className="cta-band-button">
          Browse Hotels
        </Link>
      </section>

    </div>
  )
}

export default Home