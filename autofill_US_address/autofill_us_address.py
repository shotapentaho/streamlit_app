import streamlit as st
import requests

GOOGLE_API_KEY = st.secrets["google"]["PLACES_API_KEY"]

def autocomplete_address(input_text):
    if not input_text:
        return []
    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id"
    }
    data = {
        "input": input_text,
        "locationBias": {
            "rectangle": {
                "low": {"latitude": 24.396308, "longitude": -125.0},
                "high": {"latitude": 49.384358, "longitude": -66.93457}
            }
        }
    }
    r = requests.post(url, json=data, headers=headers)
    if r.status_code == 200:
        predictions = r.json().get("places", [])
        return predictions
    else:
        st.write("Autocomplete error:", r.text)
        return []

def get_place_details(place_id):
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "id,displayName,formattedAddress,location,addresses"
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        st.write("Place details error:", r.text)
        return {}

st.title("US Address Autocomplete & Autofill (New API)")

street_input = st.text_input("Start typing street address...")

suggestions = autocomplete_address(street_input) if street_input else []

if suggestions:
    options = [s['formattedAddress'] for s in suggestions]
    selected = st.selectbox("Select Address", options)
    if selected:
        selected_idx = options.index(selected)
        place_id = suggestions[selected_idx]['id']
        details = get_place_details(place_id)
        st.write("Place details:", details)
        # You will need to adjust extraction depending on the returned "addresses" structure!
else:
    st.info("Start typing your street address to see suggestions.")