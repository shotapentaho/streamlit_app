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
        f"?place_id={place_id}&fields=address_components,formatted_address&key={GOOGLE_API_KEY}"
    )
    r = requests.get(url)
    if r.status_code == 200:
        return r.json().get('result', {})
    else:
        return {}

st.title("US Address Autocomplete & Autofill")

# 1. User types street address
street_input = st.text_input("Start typing street address...")

# 2. Show suggestions
suggestions = autocomplete_address(street_input) if street_input else []

selected = None
selected_place_id = None
if suggestions:
    options = [s['description'] for s in suggestions]
    selected = st.selectbox("Select Address", options)
    if selected:
        selected_idx = options.index(selected)
        selected_place_id = suggestions[selected_idx]['place_id']

# 3. Autofill city, state, zip
city = state = zip_code = ""
if selected_place_id:
    details = get_place_details(selected_place_id)
    components = details.get("address_components", [])
    for comp in components:
        if "locality" in comp["types"]:
            city = comp["long_name"]
        if "administrative_area_level_1" in comp["types"]:
            state = comp["short_name"]
        if "postal_code" in comp["types"]:
            zip_code = comp["long_name"]

st.text_input("City", value=city)
st.text_input("State", value=state)
st.text_input("ZIP", value=zip_code)