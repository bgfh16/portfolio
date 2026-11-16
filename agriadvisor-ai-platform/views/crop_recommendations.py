import streamlit as st
import ollama
from datetime import datetime
from components.sidebar import render_sidebar
from utils.rag import load_index, search
from utils.llm import ask
from utils.zones import ZONE_BY_STATE

@st.cache_resource(show_spinner=False)
def get_search_index():
    """Loads the search index from disk once and keeps it in memory."""
    return load_index()

# Dropdown options
# Kept here as plain lists because only this page uses them.
CROP_TYPES = [
    "Any",
    "Cereals and grains (maize, rice, millet, sorghum)",
    "Roots and tubers (cassava, yam, sweet potato)",
    "Legumes (cowpea, groundnut, soybean)",
    "Vegetables (tomato, pepper, okra, onion)",
    "Fruits (pineapple, mango, banana, citrus)",
    "Cash crops (cocoa, oil palm, cotton, cashew)",
]

STATE_PROMPT = "Select your state"

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "Federal Capital Territory (FCT)", "Gombe", "Imo", "Jigawa", "Kaduna",
    "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
    "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba",
    "Yobe", "Zamfara",
]

SEASONS = ["Rainy season", "Dry season"]

def get_current_season():
    """Rainy season runs roughly April to October; the dry season is the rest of the year."""
    return "Rainy season" if 4 <= datetime.now().month <= 10 else "Dry season"


def get_crop_recommendations(crop_type, state, season):
    """Looks up the state's zone, finds matching passages in the knowledge base,
    and asks the AI to recommend crops from them. Returns the AI's text."""
    if crop_type == "Any":
        crop_text = "any type of crop"
    else:
        crop_text = crop_type

    zone = ZONE_BY_STATE[state]

    # What to search for: the zone, the crop type, the season, and the crops-by-zone table.
    search_text = f"{zone} {crop_text} {season.lower()} main crops by zone"
    results = search(search_text, index=get_search_index(), k=4)

    passages = []
    for doc, score in results:
        passages.append(doc.page_content)
        # Shown in the terminal only, never to the user.
        print(f"[RAG] {doc.metadata['title']} - {doc.metadata['section']} ({score})")

    prompt = (
        "You are an agricultural expert advising small-scale farmers in Nigeria. "
        f"Recommend 3 to 5 crops for a farmer in {state}, Nigeria, during the {season.lower()}. "
        f"{state} is in the {zone} zone. "
        f"The farmer is interested in: {crop_text}. "
        f"Start from the crops the reference passages below list for the {zone} zone, then keep only crops of the type the farmer chose. "
        f"Use only information about the {zone} zone and ignore every other zone. "
        "Do not give planting dates or months. Do not say where information came from, and do not mention trials, reports or organisations. "
        "Do not claim anything the passages do not say. "
        "For each crop, write the crop name in bold, followed by one or two sentences "
        "explaining why it suits that zone and season. "
        "If a crop needs irrigation or a water source in this season, say so. "
        "Quote any figures exactly as written in the passages and never invent numbers. "
        "Always say \"small-scale farmers\", never \"smallholder\". "
        "Never mention \"passages\", \"documents\" or a \"knowledge base\". "
        "Reply with only a Markdown bulleted list, one crop per bullet. "
        "Do not include greetings, disclaimers, or closing remarks.\n\n"
        "Reference passages:\n\n" + "\n\n---\n\n".join(passages)
    )

    return ask([{"role": "user", "content": prompt}], "recommend")


def clear_crop_result():
    """Runs whenever a dropdown changes: removes the old result so the card
    never shows an answer that doesn't match the current selections."""
    st.session_state["crop_rec_result"] = None
    st.session_state["crop_rec_error"] = False


def show_crop_recommendations():
    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    st.markdown(
        '<div class="page-intro">Get crop suggestions based on your location, season and the type of crop you want to grow.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="crop-criteria-heading">Select your criteria</div>', unsafe_allow_html=True)

    # While the AI is working, the dropdowns lock so the choices can't change mid-request.
    loading = st.session_state.get("crop_rec_loading", False)

    crop_type = st.selectbox(
        "Crop type", CROP_TYPES,
        key="crop_rec_type", on_change=clear_crop_result, disabled=loading
    )

    state = st.selectbox(
        "Location",
        [STATE_PROMPT] + NIGERIAN_STATES,
        key="crop_rec_state", on_change=clear_crop_result, disabled=loading
    )

    # index= picks which option is preselected: today's season.
    season = st.selectbox(
        "Season",
        SEASONS,
        index=SEASONS.index(get_current_season()),
        key="crop_rec_season", on_change=clear_crop_result, disabled=loading
    )

    # Two-phase button: the click only sets a flag and reruns, so the disabled
    # "Getting recommendations..." state actually shows before the response generating starts.
    button_label = "Getting recommendations..." if loading else "Get recommendations"
    if st.button(button_label, disabled=(state == STATE_PROMPT or loading), key="crop_rec_button"):
        st.session_state["crop_rec_loading"] = True
        st.session_state["crop_rec_result"] = None
        st.session_state["crop_rec_error"] = False
        st.rerun()

    # Phase two: the slow AI call. On success the result is stored; on failure
    # an error flag is set. Either way the loading flag is reset and the page redraws.
    if st.session_state.get("crop_rec_loading"):
        try:
            with st.spinner("Finding the best crops for you..."):
                st.session_state["crop_rec_result"] = get_crop_recommendations(crop_type, state, season)
        except Exception:
            st.session_state["crop_rec_error"] = True
        st.session_state["crop_rec_loading"] = False
        st.rerun()

    if st.session_state.get("crop_rec_error"):
        st.error("Sorry, I couldn't get recommendations right now. Please try again in a moment.")

    # The result card. Lives in session_state, so it survives reruns until a dropdown changes.
    if st.session_state.get("crop_rec_result"):
        with st.container(key="crop_rec_result_card"):
            st.markdown("### Recommended crops")
            st.write(st.session_state["crop_rec_result"])