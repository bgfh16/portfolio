import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, CheckCircle2 } from 'lucide-react';
import './EmailConfirmed.css';

function EmailConfirmed() {
  const navigate = useNavigate();
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
    // small delay before the icon morphs, so the page doesn't feel jarring
    const confirmTimer = setTimeout(() => {
      setConfirmed(true);
    }, 600);

    // after showing the confirmed state for a few seconds, redirect home
    // since the user is already logged in at this point, home makes more
    // sense than sending them to a login page they no longer need
    const redirectTimer = setTimeout(() => {
      navigate('/');
    }, 3900);

    return () => {
      clearTimeout(confirmTimer);
      clearTimeout(redirectTimer);
    };
  }, [navigate]);

  return (
    <div className="email-confirmed-page">
      <div className="email-confirmed-card">
        <div className={`email-confirmed-icon ${confirmed ? 'is-confirmed' : ''}`}>
          <Mail className="icon-mail" size={48} strokeWidth={1.5} />
          <CheckCircle2 className="icon-check" size={48} strokeWidth={1.5} />
        </div>

        <h1>{confirmed ? 'Email Confirmed' : 'Confirming...'}</h1>
        <p>
          {confirmed
            ? 'Your account is verified and you are now logged in.'
            : 'Just a moment while we verify your email.'}
        </p>

        {confirmed && (
          <>
            <p className="email-confirmed-redirect">Redirecting you to home...</p>
            <Link to="/" className="email-confirmed-link">
              Go to Home Now
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default EmailConfirmed;