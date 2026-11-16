import streamlit as st
import html
import logging
from datetime import datetime
from components.sidebar import render_sidebar
from utils.supabase_client import get_authed_client

logger = logging.getLogger(__name__)


def format_joined_date(timestamp_str):
    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    day = dt.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{dt.strftime('%A')}, {day}{suffix} {dt.strftime('%B')}, {dt.year}"

def request_save_profile():
    """Runs the moment Save Changes is clicked. It only checks the input and
    flags the save; the actual Supabase call happens in the page body."""
    first = st.session_state.get("profile_first_name", "").strip()

    if not first:
        st.session_state["profile_message"] = ("error", "First name cannot be empty.")
        return

    st.session_state["profile_save_pending"] = True


def perform_profile_save():
    """Saves the edited name to Supabase. Runs in the page body, not a callback."""
    first = st.session_state.get("profile_first_name", "").strip()
    last = st.session_state.get("profile_last_name", "").strip()

    try:
        supabase = get_authed_client()
        result = (
            supabase.table("profiles")
            .update({"first_name": first, "last_name": last})
            .eq("id", st.session_state["user_id"])
            .execute()
        )
        if not result.data:
            raise ValueError("No profile row was updated")
    except Exception:
        logger.exception("Could not save profile")
        st.session_state["profile_message"] = ("error", "Couldn't save your changes. Please try again.")
        return

    st.session_state["profile_data"]["first_name"] = first
    st.session_state["profile_data"]["last_name"] = last
    st.session_state["user_first_name"] = first
    st.session_state["profile_first_name"] = first
    st.session_state["profile_last_name"] = last
    st.session_state["profile_message"] = ("success", "Your name has been updated.")
    st.session_state["profile_editing"] = False

def start_editing_profile():
    data = st.session_state["profile_data"]
    st.session_state["profile_first_name"] = data.get("first_name") or ""
    st.session_state["profile_last_name"] = data.get("last_name") or ""
    st.session_state["profile_editing"] = True

def cancel_editing_profile():
    st.session_state["profile_editing"] = False

def show_profile():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    st.markdown(
        '<div class="page-intro profile-intro"></div>',
        unsafe_allow_html=True
    )

    if "profile_data" not in st.session_state:
        try:
            supabase = get_authed_client()
            result = (
                supabase.table("profiles")
                .select("first_name, last_name, email, created_at")
                .eq("id", st.session_state["user_id"])
                .execute()
            )
            st.session_state["profile_data"] = result.data[0]
        except Exception:
            logger.exception("Could not load profile")
            st.error("Couldn't load your profile. Please refresh and try again.")
            return

    if st.session_state.pop("profile_save_pending", False):
        perform_profile_save()

    data = st.session_state["profile_data"]

    if "profile_first_name" not in st.session_state:
        st.session_state["profile_first_name"] = data.get("first_name") or ""
    if "profile_last_name" not in st.session_state:
        st.session_state["profile_last_name"] = data.get("last_name") or ""

    first = data.get("first_name") or ""
    last = data.get("last_name") or ""
    full_name = f"{first} {last}".strip() or "User"
    letter = html.escape(first[0].upper()) if first else "U"
    email = html.escape(data.get("email") or st.session_state.get("user_email", ""))
    joined = format_joined_date(data["created_at"]) if data.get("created_at") else "—"

    with st.container(key="profile_card"):
        st.markdown(
            f"""
            <div class="profile-avatar">{letter}</div>
            <div class="profile-name">{html.escape(full_name)}</div>
            <div class="profile-details">
                <div class="profile-detail-row"><span class="profile-detail-label">Email</span><span class="profile-detail-value">{email}</span></div>
                <div class="profile-detail-row"><span class="profile-detail-label">Date joined</span><span class="profile-detail-value">{joined}</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    message = st.session_state.pop("profile_message", None)
    if message:
        if message[0] == "success":
            st.success(message[1])
        else:
            st.error(message[1])

    if not st.session_state.get("profile_editing", False):
        st.button(
            "Edit name",
            icon=":material/edit:",
            key="profile_edit_button",
            on_click=start_editing_profile
        )
    else:
        st.markdown('<div class="crop-criteria-heading">Edit your name</div>', unsafe_allow_html=True)

        with st.form("profile_form", border=False):
            st.text_input("First name", key="profile_first_name", max_chars=50)
            st.text_input("Last name", key="profile_last_name", max_chars=50)
            col1, col2 = st.columns(2)
            with col1:
                st.form_submit_button("Save Changes", on_click=request_save_profile)
            with col2:
                st.form_submit_button("Cancel", on_click=cancel_editing_profile)