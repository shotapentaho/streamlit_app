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

# Step 1: User types street address
street_input = st.text_input("Start typing street address...", key="street_input")

# Step 2: Show suggestions as user types
suggestions = autocomplete_address(street_input) if street_input else []

# Step 3: Select suggestion
options = [s['description'] for s in suggestions]
selected_address = st.selectbox("Select Address", options, key="address_select") if options else None

# Step 4: When address is selected, fetch details
if "autofill_data" not in st.session_state:
    st.session_state.autofill_data = {"city": "", "state": "", "zip_code": ""}

if selected_address and options:
    selected_idx = options.index(selected_address)
    selected_place_id = suggestions[selected_idx]['place_id']
    details = get_place_details(selected_place_id)
    components = details.get("address_components", [])
    city = state = zip_code = ""
    for comp in components:
        if "locality" in comp["types"]:
            city = comp["long_name"]
        if "administrative_area_level_1" in comp["types"]:
            state = comp["short_name"]
        if "postal_code" in comp["types"]:
            zip_code = comp["long_name"]
    # Update session state to trigger autofill
    st.session_state.autofill_data = {"city": city, "state": state, "zip_code": zip_code}

# Step 5: Autofill text fields (editable)
city_val = st.session_state.autofill_data["city"]
state_val = st.session_state.autofill_data["state"]
zip_val = st.session_state.autofill_data["zip_code"]

city_val = st.text_input("City", value=city_val, key="city_input")
state_val = st.text_input("State", value=state_val, key="state_input")
zip_val = st.text_input("ZIP", value=zip_val, key="zip_input")