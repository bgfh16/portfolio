import { useState, useEffect } from 'react'
import { Pencil, Trash2, Plus, X } from 'lucide-react'
import { supabase } from '../../utils/supabaseClient'
import './AdminHotels.css'

const emptyForm = {
  name: '',
  city: '',
  country: '',
  description: '',
  image_url: '',
  star_rating: 5,
  price_from: '',
  facilities: '',
  sustainability_info: ''
}

function AdminHotels() {
  const [hotels, setHotels] = useState([])
  const [loading, setLoading] = useState(true)

  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const [deletingId, setDeletingId] = useState(null)
  const [confirmingDeleteId, setConfirmingDeleteId] = useState(null)

  useEffect(() => {
    fetchHotels()
  }, [])
  

  async function fetchHotels() {
    const { data, error } = await supabase
      .from('hotels')
      .select('*')
      .order('name', { ascending: true })

    if (error) console.error(error)
    setHotels(data || [])
    setLoading(false)
  }

  function openAddForm() {
    setForm(emptyForm)
    setEditingId(null)
    setShowForm(true)
    setError('')
  }

  function openEditForm(hotel) {
    setForm({
      name: hotel.name || '',
      city: hotel.city || '',
      country: hotel.country || '',
      description: hotel.description || '',
      image_url: hotel.image_url || '',
      star_rating: hotel.star_rating || 5,
      price_from: hotel.price_from || '',
      // facilities is stored as an array in the db, join it into a
      // comma separated string for easy editing in a plain text input
      facilities: (hotel.facilities || []).join(', '),
      sustainability_info: hotel.sustainability_info || ''
    })
    setEditingId(hotel.id)
    setShowForm(true)
    setError('')
  }

  function closeForm() {
    setShowForm(false)
    setEditingId(null)
    setForm(emptyForm)
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)

    const payload = {
      name: form.name,
      city: form.city,
      country: form.country,
      description: form.description,
      image_url: form.image_url,
      star_rating: Number(form.star_rating),
      price_from: Number(form.price_from),
      // split the comma separated string back into a clean array,
      // trimming whitespace and dropping any empty entries
      facilities: form.facilities.split(',').map((f) => f.trim()).filter(Boolean),
      sustainability_info: form.sustainability_info
    }

    let result
    if (editingId) {
      result = await supabase.from('hotels').update(payload).eq('id', editingId)
    } else {
      result = await supabase.from('hotels').insert(payload)
    }

    setSaving(false)

    if (result.error) {
      setError('Something went wrong saving this hotel. Please try again.')
      return
    }

    closeForm()
    fetchHotels()
    setSuccessMessage(editingId ? 'Hotel updated successfully.' : 'Hotel added successfully.')
    window.scrollTo({ top: 0, behavior: 'smooth' })
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  async function handleDelete(id) {
    setDeletingId(id)

    const { error } = await supabase.from('hotels').delete().eq('id', id)

    if (!error) {
      setHotels((prev) => prev.filter((h) => h.id !== id))
      setConfirmingDeleteId(null)
    }

    setDeletingId(null)
  }

  if (loading) {
    return <p className="admin-hotels-status">Loading hotels...</p>
  }

  return (
    <div className="admin-hotels-page">
      {successMessage && <p className="admin-success-message">{successMessage}</p>}

      <div className="admin-hotels-header">
        <div>
          <h1>Manage Hotels</h1>
          <p>Add, edit, or remove hotels from BookMyHotel</p>
        </div>
        <button className="admin-add-btn" onClick={openAddForm}>
          <Plus size={16} /> Add Hotel
        </button>
      </div>

      <div className="admin-hotels-table">
        <div className="admin-hotels-row admin-hotels-row-head">
          <span>Name</span>
          <span>City</span>
          <span>Country</span>
          <span>From</span>
          <span>Stars</span>
          <span>Actions</span>
        </div>

        {hotels.map((hotel) => (
          <div key={hotel.id} className="admin-hotels-row">
            <span>{hotel.name}</span>
            <span>{hotel.city}</span>
            <span>{hotel.country}</span>
            <span>${hotel.price_from}</span>
            <span className="admin-hotels-stars">{hotel.star_rating}★</span>
            <span className="admin-hotels-actions">
              {confirmingDeleteId === hotel.id ? (
                <span className="admin-delete-confirm">
                  <button
                    onClick={() => handleDelete(hotel.id)}
                    disabled={deletingId === hotel.id}
                    className="admin-delete-confirm-yes"
                  >
                    {deletingId === hotel.id ? 'Deleting...' : 'Confirm'}
                  </button>
                  <button
                    onClick={() => setConfirmingDeleteId(null)}
                    className="admin-delete-confirm-no"
                  >
                    Cancel
                  </button>
                </span>
              ) : (
                <>
                  <button onClick={() => openEditForm(hotel)} aria-label="Edit hotel">
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => setConfirmingDeleteId(hotel.id)}
                    aria-label="Delete hotel"
                    className="admin-hotels-delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </>
              )}
            </span>
          </div>
        ))}
      </div>

      {showForm && (
        <div className="admin-modal-overlay" onClick={closeForm}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h2>{editingId ? 'Edit Hotel' : 'Add Hotel'}</h2>
              <button onClick={closeForm} aria-label="Close">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="admin-form">
              <label>
                Hotel Name
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </label>

              <div className="admin-form-row">
                <label>
                  City
                  <input
                    type="text"
                    list="city-options"
                    value={form.city}
                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                    required
                  />
                  <datalist id="city-options">
                    {[...new Set(hotels.map((h) => h.city))].map((city) => (
                      <option key={city} value={city} />
                    ))}
                  </datalist>
                </label>

                <label>
                  Country
                  <input
                    type="text"
                    list="country-options"
                    value={form.country}
                    onChange={(e) => setForm({ ...form, country: e.target.value })}
                    required
                  />
                  <datalist id="country-options">
                    {[...new Set(hotels.map((h) => h.country))].map((country) => (
                      <option key={country} value={country} />
                    ))}
                  </datalist>
                </label>
              </div>

              <label>
                Description
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={3}
                  required
                />
              </label>

              <label>
                Image URL
                <input
                  type="text"
                  value={form.image_url}
                  onChange={(e) => setForm({ ...form, image_url: e.target.value })}
                  required
                />
              </label>

              <div className="admin-form-row">
                <label>
                  Star Rating
                  <input
                    type="number"
                    min={1}
                    max={5}
                    value={form.star_rating}
                    onChange={(e) => setForm({ ...form, star_rating: e.target.value })}
                    required
                  />
                </label>

                <label>
                  Price From ($)
                  <input
                    type="number"
                    min={0}
                    value={form.price_from}
                    onChange={(e) => setForm({ ...form, price_from: e.target.value })}
                    required
                  />
                </label>
              </div>

              <label>
                Facilities (comma separated)
                <input
                  type="text"
                  value={form.facilities}
                  onChange={(e) => setForm({ ...form, facilities: e.target.value })}
                  placeholder="Pool, Spa, Free WiFi"
                />
              </label>

              <label>
                Sustainability Info
                <textarea
                  value={form.sustainability_info}
                  onChange={(e) => setForm({ ...form, sustainability_info: e.target.value })}
                  rows={2}
                />
              </label>

              {error && <p className="admin-form-error">{error}</p>}

              <button type="submit" className="admin-form-submit" disabled={saving}>
                {saving ? 'Saving...' : editingId ? 'Save Changes' : 'Add Hotel'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminHotels