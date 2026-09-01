import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Users } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import { useAuth } from '../context/AuthContext'
import './RoomSelection.css'

// this page shows all rooms belonging to one specific hotel
// it fetches the hotel (for the header) and its rooms separately
function RoomSelection() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [hotel, setHotel] = useState(null)
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const hotelResult = await supabase
        .from('hotels')
        .select('*')
        .eq('id', id)
        .single()

      const roomsResult = await supabase
        .from('rooms')
        .select('*')
        .eq('hotel_id', id)
        .order('price_per_night', { ascending: true })

      if (hotelResult.error) console.error(hotelResult.error)
      if (roomsResult.error) console.error(roomsResult.error)

      setHotel(hotelResult.data)
      setRooms(roomsResult.data || [])
      setLoading(false)
    }

    fetchData()
  }, [id])

  // if not logged in, send to login with a message and a way back here
  // once logged in. if logged in, go straight to the booking form for
  // this specific room
  function handleSelectRoom(roomId) {
    if (!user) {
      navigate('/login', {
        state: {
          message: 'Please log in to book a room.',
          redirectTo: `/hotels/${id}/rooms/${roomId}/book`
        }
      })
    } else {
      navigate(`/hotels/${id}/rooms/${roomId}/book`)
    }
  }

  if (loading) {
    return <p className="room-selection-status">Loading rooms...</p>
  }

  if (!hotel) {
    return <p className="room-selection-status">Hotel not found.</p>
  }

  return (
    <div className="room-selection">
      <section className="room-selection-header">
        <button onClick={() => navigate(-1)} className="room-selection-back">
          <ArrowLeft size={16} />
          Back
        </button>
        <h1>Rooms at {hotel.name}</h1>
        <p>{hotel.city}, {hotel.country}</p>
      </section>

      <section className="room-list">
        {rooms.map((room) => (
          <div key={room.id} className="room-item">
            <img src={room.image_url} alt={room.room_type} className="room-item-image" />

            <div className="room-item-content">
              <h3>{room.room_type}</h3>
              <p className="room-item-description">{room.description}</p>

              <div className="room-item-meta">
                <span className="room-item-capacity">
                  <Users size={14} />
                  Up to {room.capacity} guests
                </span>
              </div>

              <div className="room-item-tags">
                {room.amenities?.map((amenity) => (
                  <span key={amenity} className="room-item-tag">{amenity}</span>
                ))}
              </div>
            </div>

            <div className="room-item-booking">
              <p className="room-item-price">
                ${room.price_per_night} <span>/ night</span>
              </p>
              <button className="room-item-button" onClick={() => handleSelectRoom(room.id)}>
                Select Room
              </button>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}

export default RoomSelection