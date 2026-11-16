import streamlit as st
import html
from components.sidebar import render_sidebar
from views.pest_guide_data import PEST_GUIDE_ENTRIES

def open_pest_detail(entry_id):
    # Remembers which entry was clicked. Runs before the page redraws.
    st.session_state["pest_selected"] = entry_id


def close_pest_detail():
    # Clears the selection so the list comes back.
    st.session_state["pest_selected"] = None
# How many cards sit side by side on desktop.
CARDS_PER_ROW = 3

BUG_ICON = (
    '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
    '<ellipse cx="12" cy="14" rx="4" ry="5.5"/><circle cx="12" cy="6.5" r="2"/>'
    '<path d="M12 8.5v11M8 12l-4-2M8 15H4M8.5 18.5L5 21M16 12l4-2M16 15h4M15.5 18.5L19 21M10.5 5L8.5 3M13.5 5l2-2"/>'
    '</svg>'
)
SHIELD_ICON = (
    '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M12 9v3.75m0-10.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.25-8.25-3.286Zm0 13.036h.008v.008H12v-.008Z"/>'
    '</svg>'
)


def pest_media_html(entry, css_class):

    image_url = entry.get("image_url")
    if image_url:
        return (
            f'<img class="{css_class}" src="{html.escape(image_url)}" '
            f'alt="{html.escape(entry["name"])}">'
        )
    icon = BUG_ICON if entry["type"] == "Pest" else SHIELD_ICON
    return f'<div class="{css_class} pest-media-icon">{icon}</div>'


def pest_badges_html(entry):
    # The Pest/Disease tag and the severity badge. The severity word
    # becomes a class (sev-high, sev-medium, sev-low) so CSS can colour it.
    severity = entry["severity"]
    return (
        '<div class="pest-card-tags">'
        f'<span class="pest-type-tag">{html.escape(entry["type"])}</span>'
        f'<span class="pest-sev-badge sev-{severity.lower()}">{html.escape(severity)} severity</span>'
        '</div>'
    )


def render_pest_card(entry):
    # One card. The container key lets CSS target each card.
    with st.container(key=f"pest_card_{entry['id']}"):
        st.markdown(
            pest_media_html(entry, "pest-card-media")
            + '<div class="pest-card-body">'
            + pest_badges_html(entry)
            + f'<div class="pest-card-name">{html.escape(entry["name"])}</div>'
            + f'<div class="pest-card-crops"><span class="pest-card-crops-label">Affects:</span> {html.escape(", ".join(entry["crops"]))}</div>'
            + '</div>',
            unsafe_allow_html=True
        )
        st.button(
            "View details",
            key=f"pest_view_{entry['id']}",
            on_click=open_pest_detail,
            args=(entry["id"],)
        )

def show_pest_guide():

    if not st.session_state.get("logged_in"):
        st.query_params["page"] = "login"
        st.rerun()

    render_sidebar()

    st.markdown(
        '<div class="page-intro pest-guide-intro">Learn to recognise common pests and diseases affecting Nigerian crops, and how to manage them.</div>',
        unsafe_allow_html=True
    )

    # If an entry has been picked, show its full details instead of the list.
    selected_id = st.session_state.get("pest_selected")
    selected_entry = next(
        (e for e in PEST_GUIDE_ENTRIES if e["id"] == selected_id), None
    )

    if selected_entry:
        st.button(
            "← Back to guide",
            key="pest_back_button",
            on_click=close_pest_detail
        )

        st.markdown(pest_media_html(selected_entry, "pest-hero-media"), unsafe_allow_html=True)

        # Credit line for the photo. Only shows if the entry has an image_credit.
        credit = selected_entry.get("image_credit")
        if credit:
            st.caption(credit)

        st.markdown(f"## {selected_entry['name']}")
        st.markdown(pest_badges_html(selected_entry), unsafe_allow_html=True)

        with st.container(key="pest_detail_card"):
            st.markdown("### Description")
            st.write(selected_entry["description"])

            st.markdown("### Symptoms")
            for point in selected_entry["symptoms"]:
                st.markdown(f"- {point}")

            st.markdown("### Affected Crops")
            st.write(", ".join(selected_entry["crops"]))

            st.markdown("### Treatment")
            for point in selected_entry["treatment"]:
                st.markdown(f"- {point}")

            st.markdown("### Prevention")
            for point in selected_entry["prevention"]:
                st.markdown(f"- {point}")

        # Stop here so the search bar and list are not drawn underneath.
        return

    st.markdown(
        '<div class="crop-criteria-heading">Find a pest or disease</div>',
        unsafe_allow_html=True
    )

    # Search bar: matches the name or any affected crop.
    search = st.text_input(
        "Search",
        placeholder="Search by pest, disease or crop",
        key="pest_search",
        label_visibility="collapsed"
    )

    # Filter tabs.
    filter_choice = st.radio(
        "Filter",
        ["All", "Pests", "Diseases", "By Crop"],
        horizontal=True,
        key="pest_filter",
        label_visibility="collapsed"
    )

    # The crop dropdown only appears when "By Crop" is chosen.
    selected_crop = None
    if filter_choice == "By Crop":
        all_crops = sorted({crop for e in PEST_GUIDE_ENTRIES for crop in e["crops"]})
        selected_crop = st.selectbox("Choose a crop", all_crops, key="pest_crop")

    # Apply the filter tab first, then the search text on top of it.
    results = PEST_GUIDE_ENTRIES
    if filter_choice == "Pests":
        results = [e for e in results if e["type"] == "Pest"]
    elif filter_choice == "Diseases":
        results = [e for e in results if e["type"] == "Disease"]
    elif filter_choice == "By Crop" and selected_crop:
        results = [e for e in results if selected_crop in e["crops"]]

    query = search.strip().lower()
    if query:
        results = [
            e for e in results
            if query in e["name"].lower()
            or any(query in crop.lower() for crop in e["crops"])
        ]
        

    if not results:
        st.write("No pests or diseases match your search.")

    # Card grid: take the results CARDS_PER_ROW at a time, one row of
    # columns per group.
    for start in range(0, len(results), CARDS_PER_ROW):
        columns = st.columns(CARDS_PER_ROW)
        for column, entry in zip(columns, results[start:start + CARDS_PER_ROW]):
            with column:
                render_pest_card(entry)