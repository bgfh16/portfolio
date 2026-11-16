import streamlit as st
import ollama
from datetime import datetime
from components.sidebar import render_sidebar
from utils.formatting import get_initial_avatar, format_relative_time, get_user_first_name
from utils.supabase_client import get_supabase_client
from utils.rag import load_index, search
from utils.llm import ask
from utils.zones import location_note

SYSTEM_PROMPT = """You are AgriAdvisor, a farming assistant for small-scale farmers in Nigeria.

How to answer:
- Answer using the reference passages given below. Use only the passages that fit the question and ignore the rest.
- When the reference passages give measurements, spacings, rates or dates, quote them exactly as written. Do not add, multiply or recalculate them.
- Only give a price if a reference passage states it. Never guess or estimate a price. If asked about cost and no price is given, say that prices change with the market and the season, and suggest checking with a local agro-dealer or an agricultural extension officer. When you do give a price, write it in naira (₦).
- Always say "small-scale farmers". Never use the word "smallholder".
- Never mention "passages", "documents" or a "knowledge base". Speak as if the knowledge is your own.
- If the passages do not cover the question, say you do not have specific Nigerian guidance on it, give a short general answer, and suggest the farmer ask a local agricultural extension officer.
- If the question is not about farming or agriculture, politely say you can only help with farming and agriculture.
- Never invent numbers. If the passages do not give a figure, leave it out instead of guessing.
- Never join figures from different sentences or sections into one statement. Give each figure together with the situation it belongs to, for example an amount per hectare for a whole season is separate from a bag guide for planting time.
- Do not explain what a fertiliser or product contains or supplies, and do not convert between units, unless a reference passage says so directly.
- When a passage gives advice for a named zone, say which zone it is for. If a "Farmer's location" line is given below, use the zone it states and give only the advice for that zone. If no such line is given, do not guess the farmer's zone.
- Never give pesticide or fungicide doses, rates or mixing amounts. Tell the farmer to follow the product label and ask a local agricultural extension officer.
- Do not say "it mentions", "according to" or name trials or reports. Just give the advice.
- Keep answers clear and practical."""

@st.cache_resource(show_spinner=False)
def get_search_index():
    """Loads the search index from disk once, then keeps it in memory so
    each question does not have to reload it."""
    return load_index()

def build_ai_messages(chat_messages):
    """Builds the list of messages sent to the AI: the instructions plus the
    reference passages for this question, then the conversation so far."""
    # Search on the latest question plus the one before it, so short
    # follow-ups like "how much does it cost?" still find the right topic.
    user_texts = [m["content"] for m in chat_messages if m["role"] == "user"]
    search_text = " ".join(user_texts[-2:])

    results = search(search_text, index=get_search_index())

    passages = []
    for doc, score in results:
        passages.append(doc.page_content)
        # Shown in the terminal only, never to the user.
        print(f"[RAG] {doc.metadata['title']} - {doc.metadata['section']} ({score})")

    # If the question names a state, tell the AI which zone it is in so it does not guess.
    note = location_note(search_text)
    if note:
        print(f"[RAG] {note}")
    system_text = SYSTEM_PROMPT
    if note:
        system_text += "\n\n" + note
    system_text += "\n\nReference passages:\n\n" + "\n\n---\n\n".join(passages)

    conversation = [{"role": m["role"], "content": m["content"]} for m in chat_messages]
    return [{"role": "system", "content": system_text}] + conversation


def request_chat_retry():
    """Runs the moment Retry is clicked: hides the error bubble and queues a retry."""
    st.session_state["retry_pending"] = True

def process_ai_reply(user_text):
    """Gets the AI reply for the conversation, saves it, titles the chat if needed,
    then reruns the page. If the AI call fails, it flags the failure and reruns instead."""
    supabase = get_supabase_client()
    supabase.auth.set_session(st.session_state["access_token"], st.session_state["refresh_token"])

    ai_reply = None
    ai_timestamp = None

    with st.chat_message("assistant", avatar="🌿"):
        try:
            with st.spinner("Thinking..."):
                ai_reply = ask(build_ai_messages(st.session_state["chat_messages"]), "chat")
                ai_timestamp = datetime.now().strftime("%I:%M %p")
                st.write(ai_reply)
                st.caption(ai_timestamp)
        except Exception:
            ai_reply = None

    # If the AI call failed, flag it and redraw the page so the error bubble
    # (with its Retry button) appears under the unanswered message.
    if ai_reply is None:
        st.session_state["chat_failed"] = True
        st.session_state["retry_pending"] = False
        st.rerun()

    # The reply worked, so clear any earlier failure state.
    st.session_state["chat_failed"] = False
    st.session_state["retry_pending"] = False

    try:
        supabase.table("messages").insert({
            "conversation_id": st.session_state["conversation_id"],
            "role": "assistant",
            "content": ai_reply
        }).execute()
    except Exception:
        pass

    current_convo = supabase.table("conversations").select("title").eq("id", st.session_state["conversation_id"]).execute()
    if current_convo.data[0]["title"] == "New Conversation":
        title_prompt = (
            "Write a title of 4 words or less for the question below. "
            "Do not answer the question. "
            "If the question is not about farming or agriculture, reply with exactly: General Question. "
            "Otherwise reply with the title only, nothing else.\n\n"
            f"Question: {user_text}"
        )
        try:
            raw_title = ask([{"role": "user", "content": title_prompt}], "title").strip()
        except Exception:
            raw_title = ""
        # Keep only the first line and remove quotes and end punctuation.
        first_line = raw_title.splitlines()[0].strip(' "\'.:!') if raw_title else ""
        # If the model rambled (more than 6 words), use the first words of the question instead.
        if 0 < len(first_line.split()) <= 6:
            generated_title = first_line
        else:
            generated_title = " ".join(user_text.split()[:5])
        supabase.table("conversations").update({"title": generated_title}).eq("id", st.session_state["conversation_id"]).execute()
        st.session_state["conversation_title"] = generated_title
        if "cached_conversations" in st.session_state:
            del st.session_state["cached_conversations"]

    st.session_state["chat_messages"].append({"role": "assistant", "content": ai_reply, "time": ai_timestamp})
    st.rerun()

def show_chat():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    st.markdown(
        """
        <style>
        [data-testid="stChatInput"],
        [data-testid="stBottomBlockContainer"],
        [data-testid="stMainBlockContainer"] {
            max-width: 800px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    first_name = get_user_first_name()
    user_avatar = get_initial_avatar(first_name[0].upper())

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = None

    if "conversation_title" not in st.session_state:
        st.session_state["conversation_title"] = None

    if st.session_state.get("load_conversation"):
        supabase_temp = get_supabase_client()
        supabase_temp.auth.set_session(st.session_state["access_token"], st.session_state["refresh_token"])
        try:
            messages_result = supabase_temp.table("messages").select("role, content, created_at").eq("conversation_id", st.session_state["conversation_id"]).order("created_at").execute()
            loaded_messages = []
            for msg in messages_result.data:
                time_str = datetime.fromisoformat(msg["created_at"]).strftime("%I:%M %p")
                loaded_messages.append({"role": msg["role"], "content": msg["content"], "time": time_str})
            st.session_state["chat_messages"] = loaded_messages
        except Exception:
            st.error("Couldn't load that conversation. Starting fresh instead.")
            st.session_state["chat_messages"] = []
        st.session_state["load_conversation"] = False
        st.session_state["chat_failed"] = False
        st.session_state["retry_pending"] = False

    if st.session_state["conversation_title"]:
        st.markdown(f'<div class="chat-title">{st.session_state["conversation_title"]}</div>', unsafe_allow_html=True)

    for message in st.session_state["chat_messages"]:
        avatar = user_avatar if message["role"] == "user" else "🌿"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])
            st.caption(message.get("time", ""))
    
    user_input = st.chat_input("Ask about crops, pests, or farming advice...")

    # Shown only when the last AI call failed and the last message is still unanswered.
    if (
        not user_input
        and st.session_state["chat_messages"]
        and st.session_state["chat_messages"][-1]["role"] == "user"
    ):
        with st.chat_message("assistant", avatar="🌿"):
            st.write("This message didn't get a reply. Please try again.")
            retrying = st.session_state.get("retry_pending", False)
            st.button(
                "Retrying..." if retrying else "Retry",
                key="retry_chat",
                on_click=request_chat_retry,
                disabled=retrying
            )

    # Runs on the page redraw right after Retry is clicked.
    if st.session_state.get("retry_pending") and not user_input:
        if st.session_state["chat_messages"]:
            process_ai_reply(st.session_state["chat_messages"][-1]["content"])

    if not st.session_state["chat_messages"] and not user_input:
        if "current_greeting" not in st.session_state:
            import random
            greetings = [
                f"Welcome back, {first_name}",
                f"Good to see you, {first_name}",
                f"Plant tips, {first_name}?",
                f"Ready, {first_name}?",
                f"Hey there, {first_name}",
                f"What's growing, {first_name}?",
                f"Let's farm, {first_name}",
                f"How's the farm, {first_name}?",
                f"Harvest more answers, {first_name}?",
                f"{first_name}, fields are calling",
                f"Let's dig in, {first_name}",
                f"New sprouts, {first_name}?",
                f"Let's grow, {first_name}",
                f"Rooting for you, {first_name}",
                f"Ready to cultivate, {first_name}?",
                f"What's up, {first_name}?",
                f"Here to help, {first_name}",
                f"Let's get answers, {first_name}",
                f"Thyme to farm, {first_name}",
                f"Happy planting, {first_name}"
            ]
            st.session_state["current_greeting"] = random.choice(greetings)

        st.markdown(
            f"""
            <div class="chat-welcome">
                <div class="chat-welcome-title"><span class="chat-welcome-logo">🌿</span> {st.session_state['current_greeting']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if user_input:
        timestamp = datetime.now().strftime("%I:%M %p")
        st.session_state["chat_messages"].append({"role": "user", "content": user_input, "time": timestamp})
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
            st.caption(timestamp)

        supabase = get_supabase_client()
        supabase.auth.set_session(st.session_state["access_token"], st.session_state["refresh_token"])
        try:
            if st.session_state["conversation_id"] is None:
                new_convo = supabase.table("conversations").insert({
                    "user_id": st.session_state["user_id"]
                }).execute()
                st.session_state["conversation_id"] = new_convo.data[0]["id"]
                if "cached_conversations" in st.session_state:
                    del st.session_state["cached_conversations"]    

            supabase.table("messages").insert({
                "conversation_id": st.session_state["conversation_id"],
                "role": "user",
                "content": user_input
            }).execute()
            supabase.table("conversations").update({"updated_at": "now()"}).eq("id", st.session_state["conversation_id"]).execute()
            if "cached_conversations" in st.session_state:
                del st.session_state["cached_conversations"]
        except Exception:
            pass

        # A fresh message clears any earlier failure or pending retry.
        st.session_state["chat_failed"] = False
        st.session_state["retry_pending"] = False

        process_ai_reply(user_input)
