import streamlit as st
from utils.llm import ask, ask_with_image
from components.sidebar import render_sidebar
from utils.formatting import get_initial_avatar, format_relative_time, get_user_first_name
from utils.supabase_client import get_authed_client
import html

def request_followup_retry(diagnosis_id):
    """Runs the moment a follow-up Retry is clicked: locks the page and
    queues the same question to be asked again."""
    st.session_state["any_followup_thinking"] = True
    st.session_state["pending_followup_id"] = diagnosis_id

def show_image_diagnosis():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    first_name = get_user_first_name()
    user_avatar = get_initial_avatar(first_name[0].upper())

    supabase = get_authed_client()

    if "cached_diagnoses" not in st.session_state:
        try:
            result = supabase.table("diagnoses").select("id, image_path, crop_name, full_diagnosis, updated_at").eq("user_id", st.session_state["user_id"]).order("updated_at", desc=True).execute()
            fetched = result.data
            for d in fetched:
                signed = supabase.storage.from_("diagnosis-images").create_signed_url(d["image_path"], 21600)
                d["image_url"] = signed["signedURL"]
            st.session_state["cached_diagnoses"] = fetched
        except Exception:
            st.session_state["cached_diagnoses"] = []

    diagnoses_list = st.session_state["cached_diagnoses"]

    st.markdown(
        '<div class="page-intro">Upload a photo of your crop to identify pests, diseases, or other issues.</div>',
        unsafe_allow_html=True
    )

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        help="Maximum file size: 5MB",
        key=f"crop_uploader_{st.session_state['uploader_key']}",
        disabled=st.session_state.get("diagnosing", False)
    )

    if uploaded_file is not None and uploaded_file.size > 5 * 1024 * 1024:
        st.error("File is too large. Please upload an image under 5MB.")
        uploaded_file = None

    if uploaded_file is not None:
        if st.session_state.get("last_uploaded_name") != uploaded_file.name:
            st.session_state["diagnosis_result"] = None
            st.session_state["last_uploaded_name"] = uploaded_file.name
            for diag_item in st.session_state.get("cached_diagnoses", []):
                st.session_state[f"expanded_{diag_item['id']}"] = False

        with st.container(key="uploaded_crop_image"):
            st.image(uploaded_file, caption="", width=400)

        if "diagnosing" not in st.session_state:
            st.session_state["diagnosing"] = False

        button_label = "Diagnosing..." if st.session_state["diagnosing"] else "Diagnose"
        if st.button(button_label, disabled=st.session_state["diagnosing"], key="diagnose_button"):
            st.session_state["diagnosing"] = True
            st.session_state["pending_upload"] = uploaded_file.getbuffer()
            st.rerun()

        if st.session_state["diagnosing"]:
            import uuid
            import os
            temp_filename = f"temp_upload_{uuid.uuid4().hex}.jpg"
            with open(temp_filename, "wb") as f:
                f.write(st.session_state["pending_upload"])

            diagnosis = None
            try:
                with st.spinner("Analyzing your photo..."):
                    diagnosis_prompt = (
                                    "You are an agricultural expert specializing in Nigerian crops and farming conditions. "
                                    "First, determine whether this image shows any part of a plant, crop, or agricultural produce — "
                                    "including fruits, vegetables, leaves, stems, stalks, or roots, whether healthy or visibly damaged/diseased/rotting, "
                                    "and including close-up photos of split, discoloured or decayed stalks and stems. "
                                    "If the image clearly shows none of these (for example, if it shows people, buildings, vehicles, or "
                                    "unrelated objects), respond with ONLY this exact message and nothing else: "
                                    "\"This image doesn't appear to show a crop, plant, or agricultural produce. Please upload a clear photo "
                                    "of the plant or produce you'd like diagnosed and try again.\" "
                                    "If there is any reasonable possibility the image shows a plant, crop, fruit, vegetable, or "
                                    "agricultural produce — even if partially obscured, damaged, or unclearly photographed — "
                                    "proceed with the diagnosis rather than rejecting it. Only use the rejection message if the "
                                    "image clearly and unambiguously shows something entirely unrelated, such as people, vehicles, "
                                    "buildings, or objects with no connection to agriculture. "
                                    "If it DOES show a plant, crop, or agricultural produce, examine it carefully and identify any visible pests, diseases, "
                                    "nutrient deficiencies, or other health issues. Speak with confidence and authority based on what "
                                    "is visible — avoid hedging language like 'appears to be', 'might', 'could indicate', or 'possibly'. "
                                    "State your observations and conclusions directly, as an expert would. Do not include any disclaimers "
                                    "about your capabilities or limitations. Structure your response using these exact numbered section "
                                    "headers, each on its own line: "
                                    "1) **Observations:** followed by what you see in the image, written as a short paragraph. "
                                    "2) **Most Likely Issues:** followed by the most likely problem(s) affecting the plant or produce, "
                                    "written as a short paragraph. "
                                    "3) **Possible Causes:** followed by likely causes, written as a short paragraph. "
                                    "4) **Recommended Remedies:** followed by one short introductory sentence summarizing the overall "
                                    "treatment approach, then a bulleted list of specific treatments commonly available to small-scale "
                                    "farmers in Nigeria, with each remedy on its own line as a standard Markdown bullet point (starting with -). "
                                    "Do not give brand names, doses or application rates; name only the type of treatment, and where a chemical is "
                                    "involved, say to follow the product label and ask a local agricultural extension officer. "
                                    "Begin your reply directly with the first section header, with no introduction."
                    )
                    diagnosis = ask_with_image(diagnosis_prompt, bytes(st.session_state["pending_upload"]), temperature=0)
                    st.session_state["diagnosis_result"] = diagnosis
            except Exception:
                diagnosis = None

            # If the photo analysis failed, clean up and unlock the page
            # so the user can simply try again.
            if diagnosis is None:
                st.session_state["diagnosis_failed"] = True
                os.remove(temp_filename)
                st.session_state["diagnosing"] = False
                st.rerun()

            try:
                title_prompt = f"Based on this diagnosis, give a short crop and issue name in 5 words or less, formatted as 'Crop — Issue' (no extra text): {diagnosis}"
                try:
                    crop_name = ask([{"role": "user", "content": title_prompt}], "title").strip()
                except Exception:
                    crop_name = "Crop diagnosis"

                storage_path = f"{st.session_state['user_id']}/{uuid.uuid4().hex}.jpg"
                with open(temp_filename, "rb") as f:
                    supabase.storage.from_("diagnosis-images").upload(
                        storage_path,
                        f.read(),
                        file_options={"content-type": "image/jpeg"}
                    )

                new_diagnosis = supabase.table("diagnoses").insert({
                    "user_id": st.session_state["user_id"],
                    "image_path": storage_path,
                    "crop_name": crop_name,
                    "full_diagnosis": diagnosis
                }).execute()

                new_id = new_diagnosis.data[0]["id"]
                st.session_state[f"expanded_{new_id}"] = True
                st.session_state["uploader_key"] += 1

                if "cached_diagnoses" in st.session_state:
                    del st.session_state["cached_diagnoses"]
            except Exception as e:
                st.session_state["diagnosis_save_error"] = str(e)
                st.session_state["diagnosis_result"] = diagnosis

            import os
            os.remove(temp_filename)

            st.session_state["diagnosing"] = False
            st.rerun()

        if st.session_state.get("diagnosis_failed"):
            st.error("Sorry, I couldn't analyze your photo right now. Please try again in a moment.")
            st.session_state["diagnosis_failed"] = False

        if st.session_state.get("diagnosis_save_error") and st.session_state.get("diagnosis_result"):
            st.warning(f"Couldn't save this diagnosis to your history: {st.session_state['diagnosis_save_error']}")
            st.write(st.session_state["diagnosis_result"])
            st.session_state["diagnosis_save_error"] = None
            st.session_state["diagnosis_result"] = None

    open_id = None

    if diagnoses_list:
        st.markdown('<div class="diagnoses-heading">Recent Diagnosis</div>', unsafe_allow_html=True)

        for diag in diagnoses_list:
            if f"expanded_{diag['id']}" not in st.session_state:
                st.session_state[f"expanded_{diag['id']}"] = False
            is_active = st.session_state[f"expanded_{diag['id']}"]
            row_key = f"diag_row_{diag['id']}" + ("_active" if is_active else "")
            with st.container(key=row_key):
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.image(diag["image_url"], width=72)
                with col2:
                    st.markdown(f'<div class="diagnosis-crop-name">{html.escape(diag["crop_name"])}</div>', unsafe_allow_html=True)
                    time_ago = format_relative_time(diag["updated_at"])
                    st.markdown(f'<div class="diagnosis-date">{time_ago}</div>', unsafe_allow_html=True)
                with col3:
                    if f"confirm_delete_{diag['id']}" not in st.session_state:
                        st.session_state[f"confirm_delete_{diag['id']}"] = False

                    if not st.session_state[f"confirm_delete_{diag['id']}"]:
                        view_label = "Hide" if st.session_state[f"expanded_{diag['id']}"] else "View"
                        if st.button(view_label, key=f"view_{diag['id']}", disabled=st.session_state.get("any_followup_thinking", False)):
                            currently_open = st.session_state[f"expanded_{diag['id']}"]
                            for diag_item in diagnoses_list:
                                st.session_state[f"expanded_{diag_item['id']}"] = False
                            st.session_state[f"expanded_{diag['id']}"] = not currently_open
                            st.rerun()
                        if st.button("", icon=":material/delete:", key=f"delete_{diag['id']}"):
                            st.session_state[f"confirm_delete_{diag['id']}"] = True
                            st.rerun()
                    else:
                        if st.button("Delete", icon=":material/check:", key=f"confirm_delete_yes_{diag['id']}"):
                            supabase.storage.from_("diagnosis-images").remove([diag["image_path"]])
                            supabase.table("diagnoses").delete().eq("id", diag["id"]).execute()
                            del st.session_state["cached_diagnoses"]
                            st.rerun()
                        if st.button("Cancel", icon=":material/close:", key=f"confirm_delete_no_{diag['id']}"):
                            st.session_state[f"confirm_delete_{diag['id']}"] = False
                            st.rerun()

            if st.session_state[f"expanded_{diag['id']}"]:
                open_id = diag["id"]
    else:
        st.markdown('<div class="diagnoses-heading">Recent Diagnosis</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="history-empty">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="history-empty-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"/><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z"/></svg>
                <div class="history-empty-text">You haven't diagnosed any crops yet. Upload a photo above to see your diagnoses here.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if open_id:
        open_diag = next((d for d in diagnoses_list if d["id"] == open_id), None)
        if open_diag:
            st.markdown('<div class="diagnosis-divider"></div>', unsafe_allow_html=True)
            with st.container(key="diagnosis_detail"):
                st.image(open_diag["image_url"], width=300)
                st.markdown(f"### {open_diag['crop_name']}")
                st.write(open_diag["full_diagnosis"])

                followup_key = f"followup_messages_{open_diag['id']}"
                if followup_key not in st.session_state:
                    try:
                        followup_result = supabase.table("diagnosis_followups").select("role, content").eq("diagnosis_id", open_diag["id"]).order("created_at").execute()
                        st.session_state[followup_key] = [{"role": m["role"], "content": m["content"]} for m in followup_result.data]
                    except Exception:
                        st.session_state[followup_key] = []

                for msg in st.session_state[followup_key]:
                    avatar = user_avatar if msg["role"] == "user" else "🌿"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.write(msg["content"])

                if st.session_state.get("followup_error_id") == open_diag["id"]:
                    with st.chat_message("assistant", avatar="🌿"):
                        st.write("Sorry, I couldn't get a response right now. Please try again in a moment.")
                        retrying = st.session_state.get("pending_followup_id") == open_diag["id"]
                        st.button(
                            "Retrying..." if retrying else "Retry",
                            key=f"retry_followup_{open_diag['id']}",
                            on_click=request_followup_retry,
                            args=(open_diag["id"],),
                            disabled=retrying
                        )

                if st.session_state.get("pending_followup_id") == open_diag["id"]:
                    with st.chat_message("assistant", avatar="🌿"):
                        st.write("Thinking...")

            followup_input = st.chat_input(
                "Ask a follow-up about this diagnosis...",
                key=f"followup_input_{open_diag['id']}",
                disabled=st.session_state.get("any_followup_thinking", False)
            )
            if followup_input:
                st.session_state[followup_key].append({"role": "user", "content": followup_input})
                try:
                    supabase.table("diagnosis_followups").insert({
                        "diagnosis_id": open_diag["id"],
                        "role": "user",
                        "content": followup_input
                    }).execute()
                except Exception:
                    pass
                st.session_state["followup_error_id"] = None
                st.session_state["any_followup_thinking"] = True
                st.session_state["pending_followup_id"] = open_diag["id"]
                st.rerun()

    pending_id = st.session_state.get("pending_followup_id")
    if pending_id:
        pending_diag = next((d for d in diagnoses_list if d["id"] == pending_id), None)
        followup_key = f"followup_messages_{pending_id}"
        try:
            # Clear any earlier failure; the except below sets it again if this attempt fails too.
            st.session_state["followup_error_id"] = None
            if pending_diag:
                context_messages = [
                    {"role": "system", "content": (
                        "You are AgriAdvisor, a farming assistant for small-scale farmers in Nigeria. "
                        "The farmer is asking follow-up questions about the diagnosis below. "
                        "Answer in short plain paragraphs or a short bulleted list, in under 150 words. "
                        "Do not use tables, headings or checklists. "
                        "Never give pesticide or fungicide doses, rates or mixing amounts. You may name types of products, "
                        "and tell the farmer to follow the product label and ask a local agricultural extension officer "
                        "about approved products and amounts. "
                        "Always say \"small-scale farmers\", never \"smallholder\". "
                        f"Diagnosis for reference:\n{pending_diag['full_diagnosis']}"
                    )}
                ] + st.session_state[followup_key]
                followup_reply = ask(context_messages, "chat")
                st.session_state[followup_key].append({"role": "assistant", "content": followup_reply})

                try:
                    supabase.table("diagnosis_followups").insert({
                        "diagnosis_id": pending_id,
                        "role": "assistant",
                        "content": followup_reply
                    }).execute()
                    supabase.table("diagnoses").update({"updated_at": "now()"}).eq("id", pending_id).execute()
                    if "cached_diagnoses" in st.session_state:
                        del st.session_state["cached_diagnoses"]
                except Exception:
                    pass
        except Exception:
            st.session_state["followup_error_id"] = pending_id
        finally:
            st.session_state["pending_followup_id"] = None
            st.session_state["any_followup_thinking"] = False
        st.rerun()