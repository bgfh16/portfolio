import json
import logging
import time
import streamlit as st
from supabase import create_client

logger = logging.getLogger(__name__)


def get_supabase_client():
    """Creates and returns a Supabase client using credentials from secrets.toml.

    A new client is created on every call on purpose. Do not cache or share it
    between users, because set_session() stores one user's login on the client.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception as e:
        logger.exception("Supabase credentials are missing from secrets.toml")
        raise RuntimeError("Supabase credentials are missing. Check .streamlit/secrets.toml.") from e
    return create_client(url, key)

"""
What this does: window.parent.document.cookie = "..." writes a cookie directly onto the actual page 
(reaching through the iframe via parent).
max-age=604800 sets the cookie to expire after 7 days (60×60×24×7 seconds) — meaning the user stays 
logged in for a week without re-entering credentials, a reasonable session length.

"""

def set_auth_cookies(access_token, refresh_token):
    """Saves the user's session tokens into browser cookies so login persists across page reloads.
    Cookies last 7 days (max-age=604800). Secure is added automatically on HTTPS."""
    st.iframe(
        f"""
        <script>
        const secure = window.parent.location.protocol === "https:" ? "; Secure" : "";
        const attrs = "; path=/; max-age=604800; SameSite=Lax" + secure;
        window.parent.document.cookie = "sb_access_token=" + encodeURIComponent({json.dumps(access_token)}) + attrs;
        window.parent.document.cookie = "sb_refresh_token=" + encodeURIComponent({json.dumps(refresh_token)}) + attrs;
        </script>
        """,
        height=1
    )


def clear_auth_cookies():
    """Clears the saved login cookies so the user is fully logged out."""
    st.iframe(
        """
        <script>
        const secure = window.parent.location.protocol === "https:" ? "; Secure" : "";
        const attrs = "; path=/; max-age=0; SameSite=Lax" + secure;
        window.parent.document.cookie = "sb_access_token=" + attrs;
        window.parent.document.cookie = "sb_refresh_token=" + attrs;
        </script>
        """,
        height=1
    )


def _is_network_error(error):
    """True if the error looks like a connection problem rather than a bad login."""
    name = type(error).__name__.lower()
    return any(word in name for word in (
        "retryable", "timeout", "connect", "network",
        "readerror", "writeerror", "remoteprotocol",
    ))


def get_authed_client():
    """Returns a Supabase client signed in as the current user.

    If the access token had expired and Supabase issued new tokens, they are
    saved to session_state and the cookies so they never go out of sync.
    If the session can't be restored, the user is sent to the login page.
    """
    supabase = get_supabase_client()
    access = st.session_state.get("access_token", "")
    refresh = st.session_state.get("refresh_token", "")
    session = None
    network_problem = False
    for attempt in range(3):
        try:
            supabase.auth.set_session(access, refresh)
            session = supabase.auth.get_session()
            if session is None:
                raise RuntimeError("No session after set_session")
            break
        except Exception as e:
            network_problem = _is_network_error(e)
            logger.exception("Session could not be restored (attempt %s of 3)", attempt + 1)
            if not network_problem:
                break
            if attempt < 2:
                time.sleep(1)

    if session is None:
        if network_problem:
            # The connection is the problem, not the login: keep the user logged in.
            st.error("Couldn't reach the server. Check your connection and refresh the page.")
            st.stop()
        clear_auth_cookies()
        st.session_state.clear()
        st.session_state["logged_in"] = False
        st.query_params["page"] = "login"
        st.rerun()

    if session.access_token != access or session.refresh_token != refresh:
        st.session_state["access_token"] = session.access_token
        st.session_state["refresh_token"] = session.refresh_token
        set_auth_cookies(session.access_token, session.refresh_token)
    return supabase