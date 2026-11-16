"""Which agro-ecological zone each Nigerian state belongs to.

Used by Crop Recommendations (to pick the zone for the chosen state) and by
Chat (to tell the AI which zone a state in the question belongs to, so the
AI does not have to guess).
"""

import re

# Each state's main agro-ecological zone, from the NAERLS list in our knowledge base.
# Zone borders do not follow state borders, so this is a starting point only.
ZONE_BY_STATE = {
    "Yobe": "Sahel savanna",
    "Borno": "Sudan savanna", "Jigawa": "Sudan savanna", "Kano": "Sudan savanna",
    "Katsina": "Sudan savanna", "Zamfara": "Sudan savanna", "Sokoto": "Sudan savanna",
    "Kebbi": "Sudan savanna",
    "Kaduna": "Northern Guinea savanna", "Bauchi": "Northern Guinea savanna",
    "Gombe": "Northern Guinea savanna",
    "Niger": "Southern Guinea savanna", "Adamawa": "Southern Guinea savanna",
    "Nasarawa": "Derived savanna", "Kwara": "Derived savanna",
    "Federal Capital Territory (FCT)": "Derived savanna", "Plateau": "Derived savanna",
    "Kogi": "Derived savanna", "Benue": "Derived savanna", "Taraba": "Derived savanna",
    "Oyo": "Humid forest", "Osun": "Humid forest", "Ogun": "Humid forest",
    "Ekiti": "Humid forest", "Enugu": "Humid forest", "Lagos": "Humid forest",
    "Ondo": "Humid forest", "Edo": "Humid forest", "Delta": "Humid forest",
    "Bayelsa": "Humid forest", "Rivers": "Humid forest", "Anambra": "Humid forest",
    "Imo": "Humid forest", "Ebonyi": "Humid forest", "Abia": "Humid forest",
    "Akwa Ibom": "Humid forest", "Cross River": "Humid forest",
}

# Other names people use for a state in a question.
ALIASES = {
    "FCT": "Federal Capital Territory (FCT)",
    "Abuja": "Federal Capital Territory (FCT)",
}


def states_in(text):
    """Returns the Nigerian states named in the text, in the order the list is checked.
    Whole words only, so 'Niger' matches 'Niger State' but not 'Nigeria'."""
    found = []
    for name in list(ZONE_BY_STATE) + list(ALIASES):
        if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text, re.IGNORECASE):
            state = ALIASES.get(name, name)
            if state not in found:
                found.append(state)
    return found


def location_note(text):
    """A one-line note for the AI, such as "Farmer's location: Kano is in the
    Sudan savanna zone." Returns an empty string if no state is named."""
    states = states_in(text)
    if not states:
        return ""
    parts = [f"{state} is in the {ZONE_BY_STATE[state]} zone" for state in states]
    return "Farmer's location: " + "; ".join(parts) + "."
