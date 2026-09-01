import { useState, useEffect } from 'react'
import { Pencil, Trash2, Plus, X } from 'lucide-react'
import { supabase } from '../../utils/supabaseClient'
import './AdminServices.css'

const emptyForm = {
  hotel_id: '',
  name: '',
  description: '',
  price: ''
}

function AdminServices() {
  const [services, setServices] = useState([])
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
    fetchData()
  }, [])

  async function fetchData() {
    const servicesResult = await supabase
      .from('services')
      .select('*, hotels ( name, city )')
      .order('created_at', { ascending: false })

    const hotelsResult = await supabase
      .from('hotels')
      .select('id, name, city')
      .order('name', { ascending: true })

    if (servicesResult.error) console.error(servicesResult.error)
    if (hotelsResult.error) console.error(hotelsResult.error)

    setServices(servicesResult.data || [])
    setHotels(hotelsResult.data || [])
    setLoading(false)
  }

  function openAddForm() {
    setForm(emptyForm)
    setEditingId(null)
    setShowForm(true)
    setError('')
  }

  function openEditForm(service) {
    setForm({
      hotel_id: service.hotel_id,
      name: service.name,
      description: service.description || '',
      price: service.price
    })
    setEditingId(service.id)
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

    if (!form.hotel_id) {
      setError('Please select a hotel')
      return
    }

    setSaving(true)

    const payload = {
      hotel_id: form.hotel_id,
      name: form.name,
      description: form.description,
      price: Number(form.price)
    }

    let result
    if (editingId) {
      result = await supabase.from('services').update(payload).eq('id', editingId)
    } else {
      result = await supabase.from('services').insert(payload)
    }

    setSaving(false)

    if (result.error) {
      setError('Something went wrong saving this service. Please try again.')
      return
    }

    closeForm()
    fetchData()
    setSuccessMessage(editingId ? 'Service updated successfully.' : 'Service added successfully.')
    window.scrollTo({ top: 0, behavior: 'smooth' })
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  async function handleDelete(id) {
    setDeletingId(id)

    const { error } = await supabase.from('services').delete().eq('id', id)

    if (!error) {
      setServices((prev) => prev.filter((s) => s.id !== id))
      setConfirmingDeleteId(null)
      setSuccessMessage('Service deleted successfully.')
      window.scrollTo({ top: 0, behavior: 'smooth' })
      setTimeout(() => setSuccessMessage(''), 3000)
    }

    setDeletingId(null)
  }

  if (loading) {
    return <p className="admin-svc-status">Loading services...</p>
  }

  return (
    <div className="admin-svc-page">
      {successMessage && <p className="admin-success-message">{successMessage}</p>}

      <div className="admin-svc-header">
        <div>
          <h1>Manage Services</h1>
          <p>Add, edit, or remove additional services offered by each hotel</p>
        </div>
        <button className="admin-add-btn" onClick={openAddForm}>
          <Plus size={16} /> Add Service
        </button>
      </div>

      <div className="admin-svc-table">
        <div className="admin-svc-row admin-svc-row-head">
          <span>Service</span>
          <span>Hotel</span>
          <span>Price</span>
          <span>Actions</span>
        </div>

        {services.map((service) => (
          <div key={service.id} className="admin-svc-row">
            <span>
              <span className="admin-svc-name">{service.name}</span>
              {service.description && (
                <span className="admin-svc-desc">{service.description}</span>
              )}
            </span>
            <span className="admin-svc-hotel">
              <span className="admin-svc-hotel-name">{service.hotels?.name}</span>
              <span className="admin-svc-hotel-city">{service.hotels?.city}</span>
            </span>
            <span>${service.price}</span>
            <span className="admin-svc-actions">
              {confirmingDeleteId === service.id ? (
                <span className="admin-delete-confirm">
                  <button
                    onClick={() => handleDelete(service.id)}
                    disabled={deletingId === service.id}
                    className="admin-delete-confirm-yes"
                  >
                    {deletingId === service.id ? 'Deleting...' : 'Confirm'}
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
                  <button onClick={() => openEditForm(service)} aria-label="Edit service">
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => setConfirmingDeleteId(service.id)}
                    aria-label="Delete service"
                    className="admin-svc-delete"
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
              <h2>{editingId ? 'Edit Service' : 'Add Service'}</h2>
              <button onClick={closeForm} aria-label="Close">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="admin-form">
              <label>
                Hotel
                <select
                  value={form.hotel_id}
                  onChange={(e) => setForm({ ...form, hotel_id: e.target.value })}
                  required
                >
                  <option value="">Select a hotel</option>
                  {hotels.map((hotel) => (
                    <option key={hotel.id} value={hotel.id}>
                      {hotel.name} — {hotel.city}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Service Name
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Spa Access"
                  required
                />
              </label>

              <label>
                Description (optional)
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={2}
                />
              </label>

              <label>
                Price ($)
                <input
                  type="number"
                  min={0}
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                  required
                />
              </label>

              {error && <p className="admin-form-error">{error}</p>}

              <button type="submit" className="admin-form-submit" disabled={saving}>
                {saving ? 'Saving...' : editingId ? 'Save Changes' : 'Add Service'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminServices