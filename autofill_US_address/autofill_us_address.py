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
        return r.json().get("suggestions", [])
    else:
        st.write("Autocomplete error:", r.text)
        return []

def get_place_details(place_id):
    url = f"https://places.googleapis.com/v1/{place_id}"
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY,
    }
    params = {
        "fields": "id,formattedAddress,addresses"
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        st.write("Place details error:", r.text)
        return {}

st.title("Click-to-Autofill Address Example")

if "address_input" not in st.session_state:
    st.session_state["address_input"] = ""

address_input = st.text_input("Type your address", value=st.session_state["address_input"], key="address_input_box")

suggestions = autocomplete_address(address_input) if address_input else []

if suggestions:
    st.write("Suggestions:")
    for i, s in enumerate(suggestions):
        label = s["placePrediction"]["text"]["text"]
        place_id = s["placePrediction"]["place"]
        # Use a unique key for each button
        if st.button(label, key=f"suggestion_{i}"):
            st.session_state["address_input"] = label
            st.session_state["selected_place_id"] = place_id
            st.rerun()

if "selected_place_id" in st.session_state:
    details = get_place_details(st.session_state["selected_place_id"])
    st.write("Place details:", details)
    address = (details.get("addresses") or [{}])[0]
    city = address.get("locality", "")
    state = address.get("administrativeArea", "")
    zip_code = address.get("postalCode", "")
    st.text_input("City", value=city)
    st.text_input("State", value=state)
    st.text_input("ZIP", value=zip_code)