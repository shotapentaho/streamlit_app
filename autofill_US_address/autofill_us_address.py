import streamlit as st
import requests

GOOGLE_API_KEY = st.secrets["google"]["PLACES_API_KEY"]

def autocomplete_address(input_text):
    if not input_text:
        return []
    url = (
        f"https://maps.googleapis.com/maps/api/place/autocomplete/json"
        f"?input={input_text}&types=address&components=country:us&key={GOOGLE_API_KEY}"
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get('predictions', [])
    else:
        return []

def get_place_details(place_id):
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=address_components&key={GOOGLE_API_KEY}"
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get('result', {})
    else:
        return {}

def extract_address_components(components):
    city = state = zip_code = ""
    for comp in components:
        if "locality" in comp["types"] or "postal_town" in comp["types"]:
            city = comp["long_name"]
        elif "administrative_area_level_1" in comp["types"]:
            state = comp["short_name"]
        elif "postal_code" in comp["types"]:
            zip_code = comp["long_name"]
        # Fallback for city
        elif "sublocality" in comp["types"] and not city:
            city = comp["long_name"]
        elif "administrative_area_level_2" in comp["types"] and not city:
            city = comp["long_name"]
    return city, state, zip_code

st.title("US Address Autocomplete & Autofill")

street_input = st.text_input("Start typing street address...")

suggestions = autocomplete_address(street_input) if street_input else []
selected = None
selected_place_id = None

if suggestions:
    options = [s['description'] for s in suggestions]
    selected = st.selectbox("Select Address", options, key="address_select")
    if selected:
        selected_idx = options.index(selected)
        selected_place_id = suggestions[selected_idx]['place_id']

if "autofill_data" not in st.session_state:
    st.session_state["autofill_data"] = {"city": "", "state": "", "zip": ""}

if selected_place_id:
    details = get_place_details(selected_place_id)
    components = details.get("address_components", [])
    city, state, zip_code = extract_address_components(components)
    st.session_state["autofill_data"] = {
        "city": city, "state": state, "zip": zip_code
    }

city_val = st.session_state["autofill_data"]["city"]
state_val = st.session_state["autofill_data"]["state"]
zip_val = st.session_state["autofill_data"]["zip"]

st.text_input("City", value=city_val, key="city_input")
st.text_input("State", value=state_val, key="state_input")
st.text_input("ZIP", value=zip_val, key="zip_input")