import { useState, useEffect } from 'react'
import { Mail, Phone, MapPin } from 'lucide-react'
import { supabase } from '../utils/supabaseClient'
import { useAuth } from '../context/AuthContext'
import './Contact.css'

function Contact() {
  const { user } = useAuth()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')

  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  // if the user is logged in, pre-fill their name and email so they
  // don't have to retype details we already have, they can still edit
  // these fields in case they want to be contacted differently
  useEffect(() => {
    if (user) {
      setName(user.user_metadata?.full_name || '')
      setEmail(user.email || '')
    }
  }, [user])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    const { error } = await supabase
      .from('contact_messages')
      .insert({ name, email, subject, message })

    setSubmitting(false)

    if (error) {
      setError('Something went wrong sending your message. Please try again.')
      return
    }

    setSubmitted(true)
    setSubject('')
    setMessage('')
    // we deliberately don't clear name/email here if logged in, since
    // they would just get immediately re-filled by the effect above
    if (!user) {
      setName('')
      setEmail('')
    }
  }

  function handleSendAnother() {
    setSubject('')
    setMessage('')
    setSubmitted(false)
  }

  return (
    <div
      className="contact-page"
      style={{ backgroundImage: `url(https://images.unsplash.com/photo-1758448500688-3ababa93fd67?w=1600&q=95&auto=format&fit=crop)` }}
    >
      <div className="contact-content">

        <div className="contact-info">
          <h1>Get in Touch</h1>
          <p className="contact-intro">
            Have a question about a booking, or need help planning your stay?
            Our team is here to help.
          </p>

          <div className="contact-info-item">
            <Mail size={18} />
            <span>info@bookmyhotel.com</span>
          </div>

          <div className="contact-info-item">
            <Phone size={18} />
            <span>+971 0 000 0000</span>
          </div>

          <div className="contact-info-item">
            <MapPin size={18} />
            <span>Dubai, UAE</span>
          </div>
        </div>

        <div className="contact-form-card">
          {submitted ? (
            <div className="contact-success">
              <h2>Message Sent</h2>
              <p>Thanks for reaching out. We'll get back to you as soon as we can.</p>
              <button className="contact-send-another" onClick={handleSendAnother}>
                Send Another Message
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="contact-form">
              <label>
                Full Name
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </label>

              <label>
                Email
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </label>

              <label>
                Subject
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  required
                />
              </label>

              <label>
                Message
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={5}
                  required
                />
              </label>

              {error && <p className="contact-error">{error}</p>}

              <button type="submit" className="contact-submit" disabled={submitting}>
                {submitting ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          )}
        </div>

      </div>
    </div>
  )
}

export default Contact