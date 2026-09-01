import { Link } from 'react-router-dom'
import { MapPin, Star } from 'lucide-react'
import './HotelCard.css'

function HotelCard({ hotel }) {
  return (
    <Link to={`/hotels/${hotel.id}`} className="hotel-card">
      <img src={hotel.image_url} alt={hotel.name} className="hotel-card-image" />

      <div className="hotel-card-content">
        <h3 className="hotel-card-name">{hotel.name}</h3>

        <p className="hotel-card-location">
          <MapPin size={14} />
          {hotel.city}, {hotel.country}
        </p>

        <div className="hotel-card-rating">
          {Array.from({ length: hotel.star_rating }).map((_, index) => (
            <Star key={index} size={14} fill="var(--color-primary)" color="var(--color-primary)" />
          ))}
          <span className="hotel-card-rating-label">{hotel.star_rating}-Star Hotel</span>
        </div>

        <p className="hotel-card-price">
          From <span>${hotel.price_from}</span> / night
        </p>
      </div>
    </Link>
  )
}

export default HotelCard