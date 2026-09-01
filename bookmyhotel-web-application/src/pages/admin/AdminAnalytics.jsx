import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { DollarSign, CalendarCheck, XCircle, Users } from 'lucide-react'
import { supabase } from '../../utils/supabaseClient'
import './AdminAnalytics.css'

function AdminAnalytics() {
  const [loading, setLoading] = useState(true)

  const [totalBookings, setTotalBookings] = useState(0)
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [cancellationRate, setCancellationRate] = useState(0)
  const [totalUsers, setTotalUsers] = useState(0)
  const [hotelChartData, setHotelChartData] = useState([])

  useEffect(() => {
    fetchAnalytics()
  }, [])

  async function fetchAnalytics() {
    // pull every booking along with its hotel name, so we can both
    // calculate overall stats and group counts per hotel in one pass
    const { data: bookings, error: bookingsError } = await supabase
      .from('bookings')
      .select('status, total_price, hotels ( name )')

    const { count: usersCount, error: usersError } = await supabase
      .from('users')
      .select('*', { count: 'exact', head: true })

    if (bookingsError) console.error(bookingsError)
    if (usersError) console.error(usersError)

    const allBookings = bookings || []
    const confirmed = allBookings.filter((b) => b.status === 'confirmed')
    const cancelled = allBookings.filter((b) => b.status === 'cancelled')

    const revenue = confirmed.reduce((sum, b) => sum + Number(b.total_price), 0)
    const rate = allBookings.length > 0
      ? Math.round((cancelled.length / allBookings.length) * 100)
      : 0

    // group booking counts by hotel name for the chart, counting every
    // booking regardless of status since this is about overall popularity
    const hotelCounts = {}
    allBookings.forEach((b) => {
      const hotelName = b.hotels?.name || 'Unknown'
      hotelCounts[hotelName] = (hotelCounts[hotelName] || 0) + 1
    })

    const chartData = Object.entries(hotelCounts).map(([name, count]) => ({
      name,
      bookings: count
    }))

    setTotalBookings(allBookings.length)
    setTotalRevenue(revenue)
    setCancellationRate(rate)
    setTotalUsers(usersCount || 0)
    setHotelChartData(chartData)
    setLoading(false)
  }

  if (loading) {
    return <p className="admin-analytics-status">Loading analytics...</p>
  }

  return (
    <div className="admin-analytics-page">
      <div className="admin-analytics-header">
        <h1>Analytics Dashboard</h1>
        <p>An overview of bookings, revenue, and platform activity</p>
      </div>

      <div className="admin-analytics-stats">
        <div className="admin-stat-card">
          <div className="admin-stat-icon">
            <CalendarCheck size={22} />
          </div>
          <div>
            <p className="admin-stat-value">{totalBookings}</p>
            <p className="admin-stat-label">Total Bookings</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-icon">
            <DollarSign size={22} />
          </div>
          <div>
            <p className="admin-stat-value">${totalRevenue.toLocaleString()}</p>
            <p className="admin-stat-label">Total Revenue</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-icon">
            <XCircle size={22} />
          </div>
          <div>
            <p className="admin-stat-value">{cancellationRate}%</p>
            <p className="admin-stat-label">Cancellation Rate</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-icon">
            <Users size={22} />
          </div>
          <div>
            <p className="admin-stat-value">{totalUsers}</p>
            <p className="admin-stat-label">Registered Users</p>
          </div>
        </div>
      </div>

      <div className="admin-analytics-chart-card">
        <h2>Bookings per Hotel</h2>
        {hotelChartData.length === 0 ? (
          <p className="admin-analytics-empty">No booking data yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hotelChartData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="bookings" fill="#3D5A80" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

export default AdminAnalytics