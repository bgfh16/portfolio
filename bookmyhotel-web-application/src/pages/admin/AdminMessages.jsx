import { useState, useEffect } from 'react'
import { Mail, Calendar } from 'lucide-react'
import { supabase } from '../../utils/supabaseClient'
import './AdminMessages.css'

function AdminMessages() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMessages()
  }, [])

  async function fetchMessages() {
    const { data, error } = await supabase
      .from('contact_messages')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) console.error(error)
    setMessages(data || [])
    setLoading(false)
  }

  if (loading) {
    return <p className="admin-msg-status">Loading messages...</p>
  }

  return (
    <div className="admin-msg-page">
      <div className="admin-msg-header">
        <h1>Contact Messages</h1>
        <p>Enquiries submitted through the Contact page</p>
      </div>

      {messages.length === 0 ? (
        <p className="admin-msg-empty">No messages yet.</p>
      ) : (
        <div className="admin-msg-list">
          {messages.map((msg) => {
            const replyLink = `mailto:${msg.email}?subject=${encodeURIComponent('Re: ' + msg.subject)}&body=${encodeURIComponent('\n\n---\nOriginal message from ' + msg.name + ':\n' + msg.message)}`

            return (
              <div key={msg.id} className="admin-msg-card">
                <div className="admin-msg-top">
                  <div>
                    <p className="admin-msg-subject">{msg.subject}</p>
                    <p className="admin-msg-from">{msg.name} · {msg.email}</p>
                  </div>
                  <span className="admin-msg-date">
                    <Calendar size={13} />
                    {new Date(msg.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="admin-msg-body">{msg.message}</p>
                <a href={replyLink} className="admin-msg-reply">
                  <Mail size={14} /> Reply via Email
                </a>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default AdminMessages