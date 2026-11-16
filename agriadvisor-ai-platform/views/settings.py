import streamlit as st
import logging
import time
from components.sidebar import render_sidebar
from utils.supabase_client import get_authed_client, get_supabase_client, clear_auth_cookies

logger = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 6

def request_password_change():
    """Runs the moment Change Password is clicked. It only checks the input and
    flags the change; the Supabase calls happen in the page body."""
    current = st.session_state.get("settings_current_password", "")
    new = st.session_state.get("settings_new_password", "")
    confirm = st.session_state.get("settings_confirm_password", "")

    if not current or not new or not confirm:
        st.session_state["password_message"] = ("error", "All password fields are required.")
    elif new != confirm:
        st.session_state["password_message"] = ("error", "New passwords do not match.")
    elif len(new) < MIN_PASSWORD_LENGTH:
        st.session_state["password_message"] = (
            "error", f"New password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    else:
        st.session_state["password_change_pending"] = True


def perform_password_change():
    """Verifies the current password, then updates it. Runs in the page body."""
    current = st.session_state.get("settings_current_password", "")
    new = st.session_state.get("settings_new_password", "")
    supabase = get_authed_client()
    try:
        email = supabase.auth.get_user().user.email
    except Exception:
        logger.exception("Could not read the user's email")
        st.session_state["password_message"] = ("error", "Couldn't verify your password. Please try again.")
        return

    # 1. Check the current password with a separate client, so the logged-in session is not disturbed.
    try:
        get_supabase_client().auth.sign_in_with_password({"email": email, "password": current})
    except Exception as e:
        msg = str(e).lower()
        if "invalid login credentials" in msg:
            text = "Current password is incorrect."
        else:
            logger.exception("Could not verify current password")
            text = "Couldn't verify your password. Please try again."
        st.session_state["password_message"] = ("error", text)
        return

    # 2. Update the password for the logged-in user.
    try:
        supabase.auth.update_user({"password": new})
    except Exception as e:
        msg = str(e).lower()
        if "different from the old" in msg or "same as the old" in msg:
            text = "New password must be different from your current password."
        else:
            logger.exception("Could not change password")
            text = "Couldn't change your password. Please try again."
        st.session_state["password_message"] = ("error", text)
        return

    st.session_state["settings_current_password"] = ""
    st.session_state["settings_new_password"] = ""
    st.session_state["settings_confirm_password"] = ""
    st.session_state["password_message"] = ("success", "Your password has been changed.")


def open_clear_history():
    """Runs the moment Clear Conversation History is clicked."""
    st.session_state["clear_history_confirm"] = True


def cancel_clear_history():
    """Runs the moment Cancel is clicked in the clear-history confirmation."""
    st.session_state["clear_history_confirm"] = False


def request_clear_history():
    """Runs the moment Yes, Clear is clicked. It only flags the delete;
    the Supabase call happens in the page body."""
    st.session_state["clear_history_confirm"] = False
    st.session_state["clear_history_pending"] = True


def perform_clear_history():
    """Deletes all of the user's conversations (messages go with them) and
    resets the Chat page's saved state. Runs in the page body."""
    supabase = get_authed_client()
    try:
        supabase.table("conversations").delete().eq("user_id", st.session_state["user_id"]).execute()
    except Exception:
        logger.exception("Could not clear conversation history")
        st.session_state["history_message"] = (
            "error", "Couldn't clear your conversation history. Please try again."
        )
        return

    for key in ("cached_conversations", "current_greeting"):
        st.session_state.pop(key, None)
    st.session_state["conversation_id"] = None
    st.session_state["conversation_title"] = None
    st.session_state["chat_messages"] = []
    st.session_state["load_conversation"] = False
    st.session_state["history_message"] = ("success", "Your conversation history has been cleared.")


def open_delete_account():
    """Runs the moment Delete Account is clicked."""
    st.session_state["delete_account_confirm"] = True


def cancel_delete_account():
    """Runs the moment Cancel is clicked in the delete-account confirmation."""
    st.session_state["delete_account_confirm"] = False


def request_delete_account():
    """Runs the moment Yes, Delete is clicked. It only checks that a password
    was typed and flags the delete; the Supabase work happens in the page body."""
    password = st.session_state.get("delete_account_password", "")
    if not password:
        st.session_state["delete_message"] = ("error", "Please enter your password to delete your account.")
        return
    # Kept in its own key because the password box disappears once the confirmation closes.
    st.session_state["delete_account_password_value"] = password
    st.session_state["delete_account_confirm"] = False
    st.session_state["delete_account_pending"] = True


def perform_delete_account():
    """Deletes the user's photos, then their data and account, then logs out.
    Runs in the page body."""
    user_id = st.session_state["user_id"]
    password = st.session_state.pop("delete_account_password_value", "")
    supabase = get_authed_client()

    # 0. First, check the password with a separate client, so the logged-in session is not disturbed.
    # If it fails, nothing is deleted and the confirmation opens again.
    try:
        email = supabase.auth.get_user().user.email
        get_supabase_client().auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        if "invalid login credentials" in str(e).lower():
            text = "Incorrect password. Your account has not been deleted."
        else:
            logger.exception("Could not verify password before account deletion")
            text = "Couldn't verify your password. Please try again."
        st.session_state["delete_message"] = ("error", text)
        st.session_state["delete_account_confirm"] = True
        return

    # 1. Remove the user's diagnosis photos from storage.
    try:
        bucket = supabase.storage.from_("diagnosis-images")
        files = bucket.list(user_id, {"limit": 1000})
        paths = [f"{user_id}/{f['name']}" for f in files if f.get("name")]
        if paths:
            bucket.remove(paths)
    except Exception:
        logger.exception("Could not delete diagnosis photos")
        st.session_state["delete_message"] = ("error", "Couldn't delete your account. Please try again.")
        return

    # 2. Delete the user's data and account (the SQL function).
    try:
        supabase.rpc("delete_my_account").execute()
    except Exception:
        logger.exception("Could not delete account")
        st.session_state["delete_message"] = ("error", "Couldn't delete your account. Please try again.")
        return

    # 3. Log out, the same way the Log Out button does.
    try:
        supabase.auth.sign_out()
    except Exception:
        logger.info("Sign out after account deletion failed (the user no longer exists)")
    clear_auth_cookies()
    time.sleep(0.5)
    st.session_state.clear()
    st.session_state["logged_in"] = False
    st.session_state["account_deleted"] = True
    st.query_params["page"] = "home"
    st.rerun()


def show_settings():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    st.markdown(
        '<div class="page-intro settings-intro">Manage your password and account preferences.</div>',
        unsafe_allow_html=True
    )

    if st.session_state.pop("password_change_pending", False):
        perform_password_change()

    if st.session_state.pop("clear_history_pending", False):
        perform_clear_history()

    if st.session_state.pop("delete_account_pending", False):
        perform_delete_account()

    with st.container(key="settings_card_password"):
        st.markdown(
            '<div class="settings-card-title">Change Password</div>'
            '<div class="settings-card-text">Enter your current password, then type your new one.</div>',
            unsafe_allow_html=True
        )

        message = st.session_state.pop("password_message", None)
        if message:
            if message[0] == "success":
                st.success(message[1])
            else:
                st.error(message[1])

        with st.form("password_form", border=False):
            st.text_input("Current password", type="password", key="settings_current_password",
                          autocomplete="current-password")
            st.text_input("New password", type="password", key="settings_new_password",
                          autocomplete="new-password")
            st.text_input("Confirm new password", type="password", key="settings_confirm_password",
                          autocomplete="new-password")
            st.form_submit_button("Change Password", on_click=request_password_change)

    with st.container(key="settings_card_notifications"):
        st.markdown(
            '<div class="settings-card-title">Notification Preferences '
            '<span class="settings-badge">Coming Soon</span></div>'
            '<div class="settings-card-text">Choose how AgriAdvisor keeps you updated.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <div class="settings-toggle-row">
                <span class="settings-switch"></span>
                <span class="settings-toggle-text">
                    <span class="settings-toggle-title">Planting season reminders</span>
                    <span class="settings-toggle-desc">Get crop suggestions at the start of each season.</span>
                </span>
            </div>
            <div class="settings-toggle-row">
                <span class="settings-switch"></span>
                <span class="settings-toggle-text">
                    <span class="settings-toggle-title">New pest and disease entries</span>
                    <span class="settings-toggle-desc">Get notified when new entries are added to the guide.</span>
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with st.container(key="settings_card_history"):
        st.markdown(
            '<div class="settings-card-title">Clear Conversation History</div>'
            '<div class="settings-card-text">Delete all of your chat conversations. '
            'Your image diagnoses are not affected.</div>',
            unsafe_allow_html=True
        )

        message = st.session_state.pop("history_message", None)
        if message:
            if message[0] == "success":
                st.success(message[1])
            else:
                st.error(message[1])

        if not st.session_state.get("clear_history_confirm", False):
            st.button("Clear Conversation History", key="clear_history_open", on_click=open_clear_history)
        else:
            st.markdown(
                '<div class="settings-confirm-text">Are you sure? This will delete all your chat conversations '
                'and cannot be undone. Your image diagnoses will not be affected.</div>',
                unsafe_allow_html=True
            )
            with st.container(key="clear_history_buttons"):
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Yes, Clear", key="clear_history_yes", on_click=request_clear_history)
                with col2:
                    st.button("Cancel", key="clear_history_cancel", on_click=cancel_clear_history)

    with st.container(key="settings_card_delete"):
        st.markdown(
            '<div class="settings-card-title">Delete Account</div>'
            '<div class="settings-card-text">Permanently delete your account and all your data, '
            'including your chats and image diagnoses. This cannot be undone.</div>',
            unsafe_allow_html=True
        )

        message = st.session_state.pop("delete_message", None)
        if message:
            st.error(message[1])

        if not st.session_state.get("delete_account_confirm", False):
            st.button("Delete Account", key="delete_account_open", on_click=open_delete_account)
        else:
            st.markdown(
                '<div class="settings-confirm-text">Are you sure? Your account, chats and image diagnoses '
                'will be permanently deleted. Enter your password to confirm.</div>',
                unsafe_allow_html=True
            )
            st.text_input("Password", type="password", key="delete_account_password",
                          autocomplete="current-password")
            with st.container(key="delete_account_buttons"):
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Yes, Delete", key="delete_account_yes", on_click=request_delete_account)
                with col2:
                    st.button("Cancel", key="delete_account_cancel", on_click=cancel_delete_account)