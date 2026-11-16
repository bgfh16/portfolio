import streamlit as st
from components.sidebar import render_sidebar

def guide_item(title, body_html, link_page=None, link_text=None):
    link = ""
    if link_page:
        link = f'<a class="help-link" href="?page={link_page}" target="_self">{link_text} →</a>'
    return (
        f'<details class="help-item"><summary>{title}</summary>'
        f'<div class="help-body">{body_html}{link}</div></details>'
    )

def show_help():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    st.markdown(
        '<div class="page-intro help-intro">Learn how to get the most out of AgriAdvisor.</div>',
        unsafe_allow_html=True
    )

    guides = [
        guide_item(
            "Chat",
            '<p>Ask any farming question in plain language, for example "How do I control cassava mealybug?".</p>'
            '<ol>'
            '<li>Type your question in the box at the bottom and send it.</li>'
            '<li>Keep chatting. AgriAdvisor remembers what was said earlier in the same chat.</li>'
            '<li>Find any past chat in History and open it to continue.</li>'
            '</ol>',
            "chat", "Open Chat"
        ),
        guide_item(
            "Image Diagnosis",
            '<ol>'
            '<li>Upload a clear photo of the affected plant (JPG or PNG, up to 5MB).</li>'
            '<li>Click Diagnose and wait for the result.</li>'
            '<li>Your diagnosis is saved in your list. Use View to open or hide it.</li>'
            '<li>Ask follow-up questions about it, and delete it when you no longer need it.</li>'
            '</ol>'
            '<p>Tip: a close, well-lit photo of the affected leaf, fruit or stem gives the best result.</p>',
            "image-diagnosis", "Open Image Diagnosis"
        ),
        guide_item(
            "Crop Recommendations",
            '<ol>'
            '<li>Choose your location (all 36 states and the FCT are available).</li>'
            '<li>Check the season. It is pre-selected from today\'s date and you can change it.</li>'
            '<li>Optionally pick a crop type.</li>'
            '<li>Get 3 to 5 suggested crops, each with a reason.</li>'
            '</ol>'
            '<p>Your results are not saved, so you can run it as often as you like.</p>',
            "crop-recommendations", "Open Crop Recommendations"
        ),
        guide_item(
            "Pest Guide",
            '<ol>'
            '<li>Search by name, or browse with the All, Pests, Diseases and By Crop tabs.</li>'
            '<li>Open an entry to read its description, symptoms, affected crops, treatment and prevention.</li>'
            '</ol>'
            '<p>Each entry has a High, Medium or Low severity badge, so you can see how serious it is at a glance.</p>',
            "pest-guide", "Open Pest Guide"
        ),
    ]
    st.markdown(
        '<div class="help-group-title">How to use AgriAdvisor</div>' + "".join(guides),
        unsafe_allow_html=True
    )

    faqs = [
        guide_item("Are my chats and diagnoses private?",
                   '<p>Yes. Only you can see your own chats and diagnoses.</p>'),
        guide_item("How do I delete a chat or a diagnosis?",
                   '<p>Delete chats from History and diagnoses from Image Diagnosis. Both ask you to confirm first. '
                   'To clear all your chats at once, use Settings.</p>'),
        guide_item("Which photos work best?",
                   '<p>A clear, close-up, well-lit photo of the affected leaf, fruit or stem.</p>'),
        guide_item("Why did it say my photo is not a plant?",
                   '<p>The AI can occasionally misjudge a photo. Try a closer, clearer one.</p>'),
        guide_item("Can I change my name or password?",
                   '<p>Yes. Change your name in Profile and your password in Settings.</p>'),
        guide_item("Does it work on a phone?",
                   '<p>Yes. Some pages are still best experienced on a desktop for now.</p>'),
    ]
    st.markdown(
        '<div class="help-group-title">Frequently asked questions</div>' + "".join(faqs),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="help-group-title">Good to know</div>'
        '<div class="help-disclaimer"><ul>'
        '<li>AgriAdvisor gives practical guidance you can act on, and it works best alongside local expertise. '
        'For serious or large-scale problems, an agricultural extension officer can add an on-the-ground check.</li>'
        '<li>Photo diagnoses are a strong starting point, but a photo cannot show everything. '
        'Confirm serious problems before spending heavily on treatment.</li>'
        '<li>Always follow the product label when using any pesticide or chemical.</li>'
        '</ul></div>',
        unsafe_allow_html=True
    )