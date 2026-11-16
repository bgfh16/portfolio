from datetime import datetime

def format_relative_time(timestamp_str):
    """Converts a timestamp into a human-friendly relative description like '5 minutes ago' or 'Yesterday'."""
    dt = datetime.fromisoformat(timestamp_str)
    now = datetime.now(dt.tzinfo)
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 172800:
        return "Yesterday"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} days ago"
    else:
        return dt.strftime("%b %d, %Y")

def get_initial_avatar(letter):
    """Creates a small circular SVG avatar showing a single letter, for use as a chat avatar."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><circle cx="16" cy="16" r="16" fill="%23F59E0B"/><text x="16" y="21" font-size="14" font-family="Poppins, sans-serif" font-weight="700" fill="%23FFFFFF" text-anchor="middle">{letter}</text></svg>"""
    return f"data:image/svg+xml,{svg}"

def get_user_first_name():
    """Fetches and caches the logged-in user's first name from their profile."""
    import streamlit as st
    if "user_first_name" not in st.session_state:
        import time
        from utils.supabase_client import get_authed_client, _is_network_error
        supabase = get_authed_client()
        result = None
        for attempt in range(3):
            try:
                result = supabase.table("profiles").select("first_name").eq("id", st.session_state["user_id"]).execute()
                break
            except Exception as e:
                if not _is_network_error(e):
                    raise
                if attempt < 2:
                    time.sleep(1)
        if result is None:
            st.error("Couldn't reach the server. Check your connection and refresh the page.")
            st.stop()
        if result.data:
            st.session_state["user_first_name"] = result.data[0]["first_name"]
        else:
            st.session_state["user_first_name"] = "U"
    return st.session_state["user_first_name"]