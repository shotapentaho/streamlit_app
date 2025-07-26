import streamlit as st
import requests
import pandas as pd

GOOGLE_API_KEY = st.secrets["google"]["PLACES_API_KEY"]

def autocomplete_address(input_text):
    if not input_text:
        return []
    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": GOOGLE_API_KEY}
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
    headers = {"X-Goog-Api-Key": GOOGLE_API_KEY}
    params = {
        "fields": "id,formattedAddress,addressComponents,location"
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        st.write("Place details error:", r.text)
        return {}

def extract_address_component(components, type_name):
    for comp in components:
        if type_name in comp.get("types", []):
            return comp.get("longText", "")
    return ""

st.title("📫 Autofill US Address & Map")

if "address_input" not in st.session_state:
    st.session_state["address_input"] = ""
address_input = st.text_input("Type your address", value=st.session_state["address_input"], key="address_input_box")

if address_input != st.session_state.get("address_input", ""):
    st.session_state["address_input"] = address_input
    st.session_state.pop("selected_place_id", None)

suggestions = autocomplete_address(address_input) if address_input else []

if suggestions and "selected_place_id" not in st.session_state:
    st.info("Click a suggestion to autofill:")
    for i, s in enumerate(suggestions):
        label = s["placePrediction"]["text"]["text"]
        place_id = s["placePrediction"]["place"]
        if st.button(label, key=f"suggestion_{i}"):
            st.session_state["address_input"] = label
            st.session_state["selected_place_id"] = place_id
            st.rerun()

if "selected_place_id" in st.session_state:
    details = get_place_details(st.session_state["selected_place_id"])
    components = details.get("addressComponents", [])
    city = extract_address_component(components, "locality")
    state = extract_address_component(components, "administrative_area_level_1")
    zip_code = extract_address_component(components, "postal_code")
    st.success(f"Selected: {st.session_state['address_input']}")
    st.text_input("City", value=city, disabled=True)
    st.text_input("State", value=state, disabled=True)
    st.text_input("ZIP", value=zip_code, disabled=True)

    # Extract and display map if location is present
    location = details.get("location", {})
    lat = location.get("latitude")
    lon = location.get("longitude")

    if lat is not None and lon is not None:
        df_map = pd.DataFrame([{"lat": lat, "lon": lon}])
        st.map(df_map, zoom=15)
        # Optional: Embed Google Maps iframe
        maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=15&output=embed"
        st.markdown(
            f'<iframe width="100%" height="400" src="{maps_url}"></iframe>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No location found for this address.")