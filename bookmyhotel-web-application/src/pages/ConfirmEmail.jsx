import { Mail } from 'lucide-react';
import { Link } from 'react-router-dom';
import './ConfirmEmail.css';

function ConfirmEmail() {
  return (
    <div className="confirm-email-page">
      <div className="confirm-email-card">
        <div className="confirm-email-icon">
          <Mail size={48} strokeWidth={1.5} />
        </div>
        <h1>Check your inbox</h1>
        <p>
          We've sent a confirmation link to your email address. Click the link
          to activate your account, then come back and log in.
        </p>
        <p className="confirm-email-note">
          Didn't get the email? Check your spam folder, or try registering again.
        </p>
        <Link to="/login" className="confirm-email-link">
          Back to Login
        </Link>
      </div>
    </div>
  );
}

export default ConfirmEmail;