import { useState, useEffect } from 'react'
import { Pencil, Trash2, Plus, X } from 'lucide-react'
import { supabase } from '../../utils/supabaseClient'
import './AdminPromotions.css'

const emptyForm = {
  code: '',
  discount_percent: '',
  expires_at: '',
  is_active: true
}

function AdminPromotions() {
  const [promotions, setPromotions] = useState([])
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
    fetchPromotions()
  }, [])

  async function fetchPromotions() {
    const { data, error } = await supabase
      .from('promotions')
      .select('*')
      .order('created_at', { ascending: false })
  
    if (error) {
      console.error(error)
      setLoading(false)
      return
    }
  
    const today = new Date().toISOString().split('T')[0]
  
    // find any promotions that are still marked active but whose expiry
    // date has already passed, and deactivate them in the database
    const expiredButActive = (data || []).filter(
      (p) => p.is_active && p.expires_at && p.expires_at < today
    )
  
    if (expiredButActive.length > 0) {
      const expiredIds = expiredButActive.map((p) => p.id)
      await supabase.from('promotions').update({ is_active: false }).in('id', expiredIds)
  
      // reflect the change locally too, so the table shows correctly
      // without needing a second fetch
      const updated = (data || []).map((p) =>
        expiredIds.includes(p.id) ? { ...p, is_active: false } : p
      )
      setPromotions(updated)
    } else {
      setPromotions(data || [])
    }
  
    setLoading(false)
  }

  function openAddForm() {
    setForm(emptyForm)
    setEditingId(null)
    setShowForm(true)
    setError('')
  }

  function openEditForm(promo) {
    setForm({
      code: promo.code || '',
      discount_percent: promo.discount_percent || '',
      expires_at: promo.expires_at || '',
      is_active: promo.is_active
    })
    setEditingId(promo.id)
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
      // codes are stored uppercase so lookups later are case-insensitive
      // in practice, since we always compare against the uppercase version
      code: form.code.trim().toUpperCase(),
      discount_percent: Number(form.discount_percent),
      expires_at: form.expires_at || null,
      is_active: form.is_active
    }

    let result
    if (editingId) {
      result = await supabase.from('promotions').update(payload).eq('id', editingId)
    } else {
      result = await supabase.from('promotions').insert(payload)
    }

    setSaving(false)

    if (result.error) {
      // a unique constraint violation means this code already exists
      if (result.error.code === '23505') {
        setError('This promo code already exists. Please choose a different one.')
      } else {
        setError('Something went wrong saving this promotion. Please try again.')
      }
      return
    }

    closeForm()
    fetchPromotions()
    setSuccessMessage(editingId ? 'Promotion updated successfully.' : 'Promotion added successfully.')
    window.scrollTo({ top: 0, behavior: 'smooth' })
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  async function handleDelete(id) {
    setDeletingId(id)

    const { error } = await supabase.from('promotions').delete().eq('id', id)

    if (!error) {
      setPromotions((prev) => prev.filter((p) => p.id !== id))
      setConfirmingDeleteId(null)
      setSuccessMessage('Promotion deleted successfully.')
      window.scrollTo({ top: 0, behavior: 'smooth' })
      setTimeout(() => setSuccessMessage(''), 3000)
    }

    setDeletingId(null)
  }

  if (loading) {
    return <p className="admin-promo-status">Loading promotions...</p>
  }

  return (
    <div className="admin-promo-page">
      {successMessage && <p className="admin-success-message">{successMessage}</p>}

      <div className="admin-promo-header">
        <div>
          <h1>Manage Promotions</h1>
          <p>Create and manage discount codes guests can apply at booking</p>
        </div>
        <button className="admin-add-btn" onClick={openAddForm}>
          <Plus size={16} /> Add Promotion
        </button>
      </div>

      <div className="admin-promo-table">
        <div className="admin-promo-row admin-promo-row-head">
          <span>Code</span>
          <span>Discount</span>
          <span>Expires</span>
          <span>Status</span>
          <span>Actions</span>
        </div>

        {promotions.map((promo) => (
          <div key={promo.id} className="admin-promo-row">
            <span className="admin-promo-code">{promo.code}</span>
            <span>{promo.discount_percent}% off</span>
            <span>{promo.expires_at || 'No expiry'}</span>
            <span className={`admin-promo-status-tag ${promo.is_active ? 'active' : 'inactive'}`}>
              {promo.is_active ? 'Active' : 'Inactive'}
            </span>
            <span className="admin-promo-actions">
              {confirmingDeleteId === promo.id ? (
                <span className="admin-delete-confirm">
                  <button
                    onClick={() => handleDelete(promo.id)}
                    disabled={deletingId === promo.id}
                    className="admin-delete-confirm-yes"
                  >
                    {deletingId === promo.id ? 'Deleting...' : 'Confirm'}
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
                  <button onClick={() => openEditForm(promo)} aria-label="Edit promotion">
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => setConfirmingDeleteId(promo.id)}
                    aria-label="Delete promotion"
                    className="admin-promo-delete"
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
              <h2>{editingId ? 'Edit Promotion' : 'Add Promotion'}</h2>
              <button onClick={closeForm} aria-label="Close">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="admin-form">
              <label>
                Promo Code
                <input
                  type="text"
                  value={form.code}
                  onChange={(e) => setForm({ ...form, code: e.target.value })}
                  placeholder="SUMMER10"
                  required
                />
              </label>

              <label>
                Discount Percentage
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={form.discount_percent}
                  onChange={(e) => setForm({ ...form, discount_percent: e.target.value })}
                  required
                />
              </label>

              <label>
                Expiry Date (optional)
                <input
                  type="date"
                  value={form.expires_at}
                  onChange={(e) => setForm({ ...form, expires_at: e.target.value })}
                />
              </label>

              <label className="admin-form-checkbox">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                />
                Active
              </label>

              {error && <p className="admin-form-error">{error}</p>}

              <button type="submit" className="admin-form-submit" disabled={saving}>
                {saving ? 'Saving...' : editingId ? 'Save Changes' : 'Add Promotion'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminPromotions