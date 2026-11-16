import streamlit as st
from utils.styling import load_css
from views.homepage import show_homepage
from views.login import show_login
from views.signup import show_signup
from views.chat import show_chat
from views.history import show_history
from utils.supabase_client import get_supabase_client
from views.image_diagnosis import show_image_diagnosis
from views.crop_recommendations import show_crop_recommendations
from views.pest_guide import show_pest_guide
from views.profile import show_profile
from views.settings import show_settings
from views.help import show_help
import logging
import time
from utils.supabase_client import set_auth_cookies, _is_network_error
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AgriAdvisor",
    page_icon="🌿",
    layout="wide"
)

load_css("assets/style.css")

# This whole block is basically saying: If we don't already know the user's logged in,
# check if their browser has saved login cookies from before; if it does, try using
# those to quietly restore their session — and if that doesn't work for any reason,
# just treat them as logged out."
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    access_token = st.context.cookies.get("sb_access_token")
    refresh_token = st.context.cookies.get("sb_refresh_token")
    network_problem = False

    if access_token and refresh_token:
        # Try up to 3 times, so a slow or briefly failing connection
        # doesn't log the user out by mistake.
        for attempt in range(3):
            try:
                supabase = get_supabase_client()
                supabase.auth.set_session(access_token, refresh_token)
                session = supabase.auth.get_session()
                user = supabase.auth.get_user().user
                if session and user:
                    st.session_state["user_id"] = user.id
                    st.session_state["user_email"] = user.email
                    st.session_state["access_token"] = session.access_token
                    st.session_state["refresh_token"] = session.refresh_token
                    st.session_state["logged_in"] = True
                    # If Supabase issued new tokens, save them so the next visit works
                    if session.access_token != access_token or session.refresh_token != refresh_token:
                        set_auth_cookies(session.access_token, session.refresh_token)
                break
            except Exception as e:
                network_problem = _is_network_error(e)
                logger.exception("Could not restore session from cookies (attempt %s of 3)", attempt + 1)
                if attempt < 2:
                    time.sleep(1)

        if not st.session_state["logged_in"] and network_problem:
            # The connection is the problem, not the login: don't send them to login.
            del st.session_state["logged_in"]
            st.error("Couldn't reach the server. Check your connection and refresh the page.")
            st.stop()

if st.session_state.pop("account_deleted", False):
    st.toast("Your account has been deleted.", icon="✅")

# This reads the current page from the URL's query parameters. 
# The second argument, "home", is a default fallback — if there's 
# no page parameter in the URL at all (like when someone just visits the plain root URL),
# it defaults to "home" instead of erroring out.

# Simply put: .get("page", "home") is Python asking that box two things, in order:
# "Do you have something stored under the label 'page'?" - Answer: No, nothing's there.
# "Since it's not there, here's a backup value I'm handing you instead: 'home'. Use that."
current_page = st.query_params.get("page", "home")

PROTECTED_PAGES = {"chat","history","image-diagnosis","crop-recommendations","pest-guide","profile","settings","help"}
if current_page in PROTECTED_PAGES and not st.session_state.get("logged_in"):
    st.query_params["page"] = "login"
    st.rerun()

try:
    if current_page == "login":
        show_login()
    elif current_page == "signup":
        show_signup()
    elif current_page == "chat":
        show_chat()
    elif current_page == "history":
        show_history()
    elif current_page == "image-diagnosis":
        show_image_diagnosis()
    elif current_page == "crop-recommendations":
        show_crop_recommendations()
    elif current_page == "pest-guide":
        show_pest_guide()
    elif current_page == "profile":
        show_profile()
    elif current_page == "settings":
        show_settings()
    elif current_page == "help":
        show_help()
    else:
        show_homepage()
except Exception as e:
    if _is_network_error(e):
        logger.exception("Connection problem while showing the page")
        st.error("Couldn't reach the server. Check your connection and refresh the page.")
        st.stop()
    raise