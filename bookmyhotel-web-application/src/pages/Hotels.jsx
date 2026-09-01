import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search, Tag } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import HotelCard from '../components/HotelCard'
import './Hotels.css'

// this is the hotel listings page
// it fetches all hotels then lets the user filter by search text, country, price, services and room type
function Hotels() {
  const [searchParams] = useSearchParams()

  const [hotels, setHotels] = useState([])
  const [roomTiersByHotel, setRoomTiersByHotel] = useState({})
  const [servicesByHotel, setServicesByHotel] = useState({})
  const [loading, setLoading] = useState(true)
  const [activePromos, setActivePromos] = useState([])

  // filter state - these track what the user has typed/selected
  // searchText starts from the url's "search" param if one was passed in
  // (e.g. from the home page search bar), otherwise starts empty
  const [searchText, setSearchText] = useState(searchParams.get('search') || '')
  const [countryFilter, setCountryFilter] = useState('All')
  const [priceFilter, setPriceFilter] = useState('All')
  const [facilityFilters, setFacilityFilters] = useState([])
  const [serviceFilters, setServiceFilters] = useState([])
  const [roomTypeFilter, setRoomTypeFilter] = useState('All')

  useEffect(() => {
    async function fetchData() {
      const hotelsResult = await supabase.from('hotels').select('*')
      const roomsResult = await supabase.from('rooms').select('hotel_id, room_type')
      const servicesResult = await supabase.from('services').select('hotel_id, name')

      if (hotelsResult.error) console.error(hotelsResult.error)
      if (roomsResult.error) console.error(roomsResult.error)
      if (servicesResult.error) console.error(servicesResult.error)

      setHotels(hotelsResult.data || [])

      // build a map of hotel_id -> list of room tiers (the word inside brackets, e.g. "Deluxe")
      // this lets us filter hotels by whether they offer a specific room tier
      const tierMap = {}
      roomsResult.data?.forEach((room) => {
        const match = room.room_type.match(/\(([^)]+)\)/)
        const tier = match ? match[1] : room.room_type
        if (!tierMap[room.hotel_id]) tierMap[room.hotel_id] = []
        if (!tierMap[room.hotel_id].includes(tier)) tierMap[room.hotel_id].push(tier)
      })
      setRoomTiersByHotel(tierMap)

      // build a map of hotel_id -> list of service names it offers,
      // same pattern as room tiers, used for the services filter below
      const svcMap = {}
      servicesResult.data?.forEach((service) => {
        if (!svcMap[service.hotel_id]) svcMap[service.hotel_id] = []
        if (!svcMap[service.hotel_id].includes(service.name)) svcMap[service.hotel_id].push(service.name)
      })
      setServicesByHotel(svcMap)

      setLoading(false)
    }

    fetchData()
  }, [])

  useEffect(() => {
    async function fetchPromos() {
      const today = new Date().toISOString().split('T')[0]

      // only show codes that are genuinely still valid right now, checking
      // both flags directly rather than relying on the admin having
      // visited the promotions page recently to auto flip expired ones
      const { data, error } = await supabase
        .from('promotions')
        .select('code, discount_percent, expires_at')
        .eq('is_active', true)
        .or(`expires_at.is.null,expires_at.gte.${today}`)

      if (error) {
        console.error(error)
        return
      }

      setActivePromos(data || [])
    }

    fetchPromos()
  }, [])

  const countries = ['All', ...new Set(hotels.map((hotel) => hotel.country))]

  // build a flat, deduplicated list of every facility across all hotels
  const allFacilities = [...new Set(hotels.flatMap((hotel) => hotel.facilities || []))].sort()

  // build a flat, deduplicated list of every service name across all hotels
  const allServiceNames = [...new Set(Object.values(servicesByHotel).flat())].sort()

  // build a flat, deduplicated list of every room tier across all hotels
  const allRoomTypes = ['All', ...new Set(Object.values(roomTiersByHotel).flat())].sort()

  function toggleFacility(facility) {
    setFacilityFilters((prev) =>
      prev.includes(facility)
        ? prev.filter((f) => f !== facility)
        : [...prev, facility]
    )
  }

  function toggleServiceFilter(service) {
    setServiceFilters((prev) =>
      prev.includes(service)
        ? prev.filter((s) => s !== service)
        : [...prev, service]
    )
  }

  const filteredHotels = hotels.filter((hotel) => {
    const matchesSearch =
      hotel.name.toLowerCase().includes(searchText.toLowerCase()) ||
      hotel.city.toLowerCase().includes(searchText.toLowerCase()) ||
      hotel.country.toLowerCase().includes(searchText.toLowerCase())

    const matchesCountry =
      countryFilter === 'All' || hotel.country === countryFilter

    const matchesPrice =
      priceFilter === 'All' ||
      (priceFilter === 'Under 500' && hotel.price_from < 500) ||
      (priceFilter === '500 to 700' && hotel.price_from >= 500 && hotel.price_from <= 700) ||
      (priceFilter === 'Over 700' && hotel.price_from > 700)

    // a hotel matches only if it has every currently selected facility
    const matchesFacilities =
      facilityFilters.length === 0 ||
      facilityFilters.every((facility) => hotel.facilities?.includes(facility))

    // a hotel matches only if it offers every currently selected service
    const matchesServices =
      serviceFilters.length === 0 ||
      serviceFilters.every((service) => servicesByHotel[hotel.id]?.includes(service))

    // a hotel matches if any of its rooms belong to the selected tier
    const matchesRoomType =
      roomTypeFilter === 'All' ||
      roomTiersByHotel[hotel.id]?.includes(roomTypeFilter)

    return matchesSearch && matchesCountry && matchesPrice && matchesFacilities && matchesServices && matchesRoomType
  })

  return (
    <div className="hotels-page">
      {activePromos.length > 0 && (
        <section className="promo-banner">
          <Tag size={16} />
          <p>
            {activePromos.map((promo, i) => (
              <span key={promo.code}>
                Use code <strong>{promo.code}</strong> for{" "}
                {promo.discount_percent}% off
                {i < activePromos.length - 1 ? " · " : ""}
              </span>
            ))}
          </p>
        </section>
      )}

      <section className="hotels-header">
        <h1>Our Hotels</h1>
        <p>Browse our collection of five-star properties around the world</p>
      </section>

      <section className="filter-bar">
        <div className="filter-search">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by hotel, city or country"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>

        <select
          value={countryFilter}
          onChange={(e) => setCountryFilter(e.target.value)}
        >
          {countries.map((country) => (
            <option key={country} value={country}>
              {country}
            </option>
          ))}
        </select>

        <select
          value={priceFilter}
          onChange={(e) => setPriceFilter(e.target.value)}
        >
          <option value="All">Any Price</option>
          <option value="Under 500">Under $500</option>
          <option value="500 to 700">$500 - $700</option>
          <option value="Over 700">Over $700</option>
        </select>

        <select
          value={roomTypeFilter}
          onChange={(e) => setRoomTypeFilter(e.target.value)}
        >
          {allRoomTypes.map((tier) => (
            <option key={tier} value={tier}>
              {tier === "All" ? "Any Room Type" : tier}
            </option>
          ))}
        </select>
      </section>

      {/* facilities filter - shown as clickable chips, multiple can be selected at once */}
      <section className="filter-label-section">
        <p className="filter-label">Filter by Facilities</p>
      </section>

      <section className="service-filter-bar">
        {allFacilities.map((facility) => (
          <button
            key={facility}
            className={`service-chip ${
              facilityFilters.includes(facility) ? "service-chip-active" : ""
            }`}
            onClick={() => toggleFacility(facility)}
          >
            {facility}
          </button>
        ))}
      </section>

      {/* services filter - separate from facilities since services are paid add-ons, not included amenities */}
      {allServiceNames.length > 0 && (
        <>
          <section className="filter-label-section">
            <p className="filter-label">Filter by Services (Paid)</p>
          </section>

          <section className="service-filter-bar">
            {allServiceNames.map((service) => (
              <button
                key={service}
                className={`service-chip service-chip-alt ${
                  serviceFilters.includes(service) ? "service-chip-active" : ""
                }`}
                onClick={() => toggleServiceFilter(service)}
              >
                {service}
              </button>
            ))}
          </section>
        </>
      )}

      <section className="hotels-results">
        {loading ? (
          <p className="loading-text">Loading hotels...</p>
        ) : filteredHotels.length === 0 ? (
          <p className="no-results">
            No hotels match your search. Try adjusting your filters.
          </p>
        ) : (
          <div className="hotel-grid">
            {filteredHotels.map((hotel) => (
              <HotelCard key={hotel.id} hotel={hotel} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Hotels