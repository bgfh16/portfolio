import streamlit as st
import logging
logger = logging.getLogger(__name__)

def open_sidebar():
    """Runs the moment the ▶ button is clicked, before the page reruns."""
    st.session_state["sidebar_open"] = True


def close_sidebar():
    """Runs the moment the ◀ button is clicked, before the page reruns."""
    st.session_state["sidebar_open"] = False

def render_sidebar():

    """Renders the app's main sidebar navigation for logged-in pages."""

    if "sidebar_open" not in st.session_state:
        st.session_state["sidebar_open"] = True

    if not st.session_state["sidebar_open"]:
        st.markdown(
            "<style>[data-testid='stSidebar'] { display: none !important; z-index: -1 !important; }</style>",
            unsafe_allow_html=True
        )
        st.button("▶", key="sidebar_toggle_closed", on_click=open_sidebar)
        return
    
    current_page = st.query_params.get("page", "")

    st.iframe(
        """
        <script>
        (function () {
            const win = window.parent;
            const doc = win.document;

            if (win.__sbReopenTimer) win.clearInterval(win.__sbReopenTimer);
            const old = doc.getElementById("mobile-sidebar-reopen");
            if (old) old.remove();
            const oldStyle = doc.getElementById("mobile-sidebar-reopen-style");
            if (oldStyle) oldStyle.remove();

            const style = doc.createElement("style");
            style.id = "mobile-sidebar-reopen-style";
            style.textContent = `
                #mobile-sidebar-reopen {
                    display: none;
                    position: fixed;
                    top: 25px;
                    left: 12px;
                    z-index: 1000;
                    width: 36px;
                    height: 36px;
                    padding: 0;
                    border: none;
                    border-radius: 8px;
                    background-color: #064E3B;
                    color: #FFFFFF;
                    font-family: 'Inter', sans-serif;
                    font-size: 11px;
                    line-height: 1;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
                    cursor: pointer;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.15s ease;
                }
                #mobile-sidebar-reopen:hover,
                #mobile-sidebar-reopen:active {
                    background-color: #059669;
                }
                #mobile-sidebar-reopen:focus {
                    outline: none;
                }
            `;
            doc.head.appendChild(style);

            const btn = doc.createElement("button");
            btn.id = "mobile-sidebar-reopen";
            btn.textContent = "▶";
            doc.body.appendChild(btn);

            btn.addEventListener("click", function () {
                const expand =
                    doc.querySelector('[data-testid="stExpandSidebarButton"]') ||
                    doc.querySelector('[data-testid="stSidebarCollapsedControl"] button');
                if (expand) expand.click();
            });

            win.__sbReopenTimer = win.setInterval(function () {
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                const collapsed = sidebar && sidebar.getAttribute("aria-expanded") === "false";
                btn.style.display = collapsed ? "flex" : "none";
            }, 300);
        })();
        </script>
        """,
        height=1,
    )

    with st.sidebar:
        st.button("◀", key="sidebar_toggle", on_click=close_sidebar)
        
        st.markdown('<div class="sidebar-logo">🌿 AgriAdvisor</div>', unsafe_allow_html=True)

        chat_active = " sidebar-link-active" if current_page == "chat" else ""
        st.markdown(f'<a href="?page=chat" target="_self" class="sidebar-link{chat_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"/></svg>Chat</a>', unsafe_allow_html=True)

        history_active = " sidebar-link-active" if current_page == "history" else ""
        st.markdown(f'<a href="?page=history" target="_self" class="sidebar-link{history_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>History</a>', unsafe_allow_html=True)

        image_active = " sidebar-link-active" if current_page == "image-diagnosis" else ""
        st.markdown(f'<a href="?page=image-diagnosis" target="_self" class="sidebar-link{image_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"/><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z"/></svg>Image Diagnosis</a>', unsafe_allow_html=True)

        crop_active = " sidebar-link-active" if current_page == "crop-recommendations" else ""
        st.markdown(f'<a href="?page=crop-recommendations" target="_self" class="sidebar-link{crop_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="2 2 20 20" stroke-width="1.25" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" class="sidebar-icon"><path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/></svg>Crop Recommendations</a>', unsafe_allow_html=True)

        pest_active = " sidebar-link-active" if current_page == "pest-guide" else ""
        st.markdown(f'<a href="?page=pest-guide" target="_self" class="sidebar-link{pest_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0 1 12 12.75Zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 0 1-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75a2.25 2.25 0 0 0 2.248-2.354M12 12.75a2.25 2.25 0 0 1-2.248-2.354M12 8.25c.995 0 1.971-.08 2.922-.236.403-.066.74-.358.795-.762a3.778 3.778 0 0 0-.399-2.25M12 8.25c-.995 0-1.97-.08-2.922-.236-.402-.066-.74-.358-.795-.762a3.734 3.734 0 0 1 .4-2.253M12 8.25a2.25 2.25 0 0 0-2.248 2.146M12 8.25a2.25 2.25 0 0 1 2.248 2.146M8.683 5a6.032 6.032 0 0 1-1.155-1.002c.07-.63.27-1.222.574-1.747m.581 2.749A3.75 3.75 0 0 1 15.318 5m0 0c.427-.283.815-.62 1.155-.999a4.471 4.471 0 0 0-.575-1.752M4.921 6a24.048 24.048 0 0 0-.392 3.314c1.668.546 3.416.914 5.223 1.082M19.08 6c.205 1.08.337 2.187.392 3.314a23.882 23.882 0 0 1-5.223 1.082"/></svg>Pest & Disease Guide</a>', unsafe_allow_html=True)

        profile_active = " sidebar-link-active" if current_page == "profile" else ""
        st.markdown(f'<a href="?page=profile" target="_self" class="sidebar-link{profile_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"/></svg>Profile</a>', unsafe_allow_html=True)

        settings_active = " sidebar-link-active" if current_page == "settings" else ""
        st.markdown(f'<a href="?page=settings" target="_self" class="sidebar-link{settings_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/></svg>Settings</a>', unsafe_allow_html=True)

        help_active = " sidebar-link-active" if current_page == "help" else ""
        st.markdown(f'<a href="?page=help" target="_self" class="sidebar-link{help_active}"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="sidebar-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z"/></svg>Help</a>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if "confirm_logout" not in st.session_state:
            st.session_state["confirm_logout"] = False

        # If we're not yet confirming logout, show a normal button;
        # the moment that button's clicked, flip a flag and immediately
        # refresh — which causes the confirmation prompt to appear instead,
        # on the very next run of this same code.
        if not st.session_state["confirm_logout"]:
            if st.button("Log Out"):
                st.session_state["confirm_logout"] = True
                st.rerun()
        else:
            st.warning("Are you sure you want to log out?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Log Out", key="confirm_logout_yes"):
                    from utils.supabase_client import get_supabase_client, clear_auth_cookies
                    import time
                    try:
                        supabase = get_supabase_client()
                        supabase.auth.set_session(
                            st.session_state.get("access_token", ""),
                            st.session_state.get("refresh_token", "")
                        )
                        supabase.auth.sign_out()
                    except Exception:
                        logger.exception("Sign out failed on the server")
                    clear_auth_cookies()
                    time.sleep(0.5)
                    st.session_state.clear()
                    st.session_state["logged_in"] = False
                    st.query_params["page"] = "home"
                    st.rerun()
            with col2:
                if st.button("Cancel", key="confirm_logout_cancel"):
                    st.session_state["confirm_logout"] = False
                    st.rerun()
