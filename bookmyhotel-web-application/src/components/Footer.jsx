import { Link } from 'react-router-dom'
import { Mail, Phone, MapPin } from 'lucide-react'
import './Footer.css'

// this is the footer that shows on every page.
// It has the bookmyhotel brand info, quick links and contact details
function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">

        {/* brand column */}
        <div className="footer-column">
          <img
            src="https://txnlijkzhcmwrliivlzk.supabase.co/storage/v1/object/public/branding/logo-header2.png"
            alt="BookMyHotel"
            className="footer-logo-img"
          />
          <p className="footer-tagline">
            Five-star stays across our global collection of hotels, where comfort meets elegance.
          </p>
        </div>

        {/* quick links column */}
        <div className="footer-column">
          <h4 className="footer-heading">Quick Links</h4>
          <Link to="/" className="footer-link">Home</Link>
          <Link to="/hotels" className="footer-link">Hotels</Link>
          <Link to="/contact" className="footer-link">Contact</Link>
        </div>

        {/* contact info column */}
        <div className="footer-column">
          <h4 className="footer-heading">Contact</h4>
          <p className="footer-contact-item">
            <Mail size={16} /> info@bookmyhotel.com
          </p>
          <p className="footer-contact-item">
            <Phone size={16} /> +971 0 000 0000
          </p>
          <p className="footer-contact-item">
            <MapPin size={16} /> Dubai, UAE
          </p>
        </div>

      </div>

      {/* bottom copyright bar */}
      <div className="footer-bottom">
        <p>© 2026 BookMyHotel. All rights reserved.</p>
      </div>
    </footer>
  )
}

export default Footer