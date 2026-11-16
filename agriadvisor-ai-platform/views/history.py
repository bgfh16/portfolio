import streamlit as st
from components.sidebar import render_sidebar
from utils.supabase_client import get_authed_client
from utils.formatting import format_relative_time

def show_history():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    supabase = get_authed_client()

    if "cached_conversations" not in st.session_state:
        try:
            result = supabase.table("conversations").select("id, title, updated_at").eq("user_id", st.session_state["user_id"]).order("updated_at", desc=True).execute()
            st.session_state["cached_conversations"] = result.data
        except Exception:
            st.session_state["cached_conversations"] = []
            st.error("Couldn't load your conversation history. Please try again.")

    conversations = st.session_state["cached_conversations"]

    if not conversations:
        st.markdown(
            """
            <div class="history-empty">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="history-empty-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
                <div class="history-empty-text">You don't have any past conversations yet. Start chatting to see your history here.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    st.markdown('<div class="history-list">', unsafe_allow_html=True)
    for convo in conversations:
        formatted_date = format_relative_time(convo["updated_at"])

        with st.container(key=f"history_row_{convo['id']}"):
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.markdown(
                    """
                    <span class="history-bullet">
                        <span class="petal petal-1"></span>
                        <span class="petal petal-2"></span>
                        <span class="petal petal-3"></span>
                        <span class="petal petal-4"></span>
                    </span>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(convo["title"], key=f"open_{convo['id']}"):
                    st.session_state["conversation_id"] = convo["id"]
                    st.session_state["conversation_title"] = convo["title"]
                    st.session_state["load_conversation"] = True
                    st.query_params["page"] = "chat"
                    st.rerun()
            with col2:
                st.markdown(f'<div class="history-date">{formatted_date}</div>', unsafe_allow_html=True)
            with col3:
                if f"confirm_delete_{convo['id']}" not in st.session_state:
                    st.session_state[f"confirm_delete_{convo['id']}"] = False

                if not st.session_state[f"confirm_delete_{convo['id']}"]:
                    if st.button("", icon=":material/delete:", key=f"delete_{convo['id']}"):
                        st.session_state[f"confirm_delete_{convo['id']}"] = True
                        st.rerun()
                else:
                    if st.button("Delete", icon=":material/check:", key=f"confirm_delete_yes_{convo['id']}"):
                        supabase.table("conversations").delete().eq("id", convo["id"]).execute()
                        del st.session_state["cached_conversations"]
                        st.rerun()
                    if st.button("Cancel", icon=":material/close:", key=f"confirm_delete_no_{convo['id']}"):
                        st.session_state[f"confirm_delete_{convo['id']}"] = False
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)