import streamlit as st

def render_navbar():
    """Renders the sticky top navbar with logo and login link, adjusting for logged-in users."""
    if st.session_state.get("logged_in"):
        nav_link = '<a class="navbar-login" href="?page=chat" target="_self">Go to Chat</a>'
    else:
        nav_link = '<a class="navbar-login" href="?page=login" target="_self">Login</a>'

    st.markdown(
        f"""
        <div class="navbar">
            <div class="navbar-logo">🌿 AgriAdvisor</div>
            {nav_link}
        </div>
        """,
        unsafe_allow_html=True
    )