import streamlit as st
import requests

# Replace with your Google Places API key or Smarty US Autocomplete API credentials
GOOGLE_API_KEY = st.secrets["google"]["PLACES_API_KEY"]  # Or use your preferred secrets management

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

st.title("US Street Address Autocomplete")

street_input = st.text_input("Start typing street address...")

suggestions = []
if street_input:
    suggestions = autocomplete_address(street_input)

if suggestions:
    options = [s['description'] for s in suggestions]
    selected = st.selectbox("Select Address", options)
    st.write(f"Selected: {selected}")
else:
    st.info("Start typing your street address to see suggestions.")