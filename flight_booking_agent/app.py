from datetime import date
from html import escape
from typing import List

import streamlit as st

from agent_models import Passenger, SearchCriteria
from agents.intent_agent import IntentAgent
from agents.orchestrator import OrchestratorAgent
from secrets_loader import resolve_openai_api_key


st.set_page_config(
    page_title="Flight Booking Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp { background: #f6f8fb; }
    .block-container { max-width: 1280px; padding: 2rem 3rem 4rem; }
    .hero {
        background: linear-gradient(135deg, #102a43 0%, #1f5f8b 100%);
        border-radius: 20px; padding: 2.2rem 2.5rem; color: white;
        margin-bottom: 1.5rem; box-shadow: 0 12px 30px rgba(16, 42, 67, .16);
    }
    .hero h1 { margin: 0; color: white; font-size: 2.25rem; }
    .hero p { margin: .55rem 0 0; color: #d9eaf7; font-size: 1.05rem; }
    .section-title { color: #102a43; font-size: 1.35rem; font-weight: 700; margin: 1.4rem 0 .7rem; }
    .weather-card, .itinerary-card {
        background: white; border: 1px solid #e5eaf0; border-radius: 16px;
        padding: 1.1rem 1.25rem; height: 100%;
        box-shadow: 0 5px 16px rgba(16, 42, 67, .06);
    }
    .weather-card h4 { margin: 0; color: #102a43; }
    .weather-temp { color: #1f5f8b; font-size: 1.8rem; font-weight: 700; margin: .35rem 0; }
    .weather-meta, .flight-meta { color: #627d98; font-size: .88rem; }
    .route { color: #102a43; font-size: 1.1rem; font-weight: 700; margin: .5rem 0; }
    .flight-number { color: #627d98; font-size: .9rem; }
    .price { color: #102a43; font-size: 1.45rem; font-weight: 800; text-align: right; }
    .price-label { color: #829ab1; font-size: .76rem; text-align: right; text-transform: uppercase; letter-spacing: .06em; }
    .stButton > button[kind="primary"] { background: #1f5f8b; border-color: #1f5f8b; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _initialise_state() -> None:
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = OrchestratorAgent()
    if "intent_agent" not in st.session_state:
        st.session_state.intent_agent = IntentAgent(
            api_key=resolve_openai_api_key(set_env=True)
        )
    st.session_state.setdefault("itineraries", [])
    st.session_state.setdefault("weather_report", None)
    st.session_state.setdefault("query_signature", None)
    st.session_state.setdefault(
        "filters",
        {
            "origin": "SFO",
            "destination": "JFK",
            "depart": date.today(),
            "return_enabled": False,
            "return_date": date.today(),
            "cabin": "ECONOMY",
            "adults": 1,
            "max_results": 6,
            "price_cap": 0.0,
        },
    )


def _apply_natural_language_query(query: str) -> None:
    cleaned = query.strip()
    if not cleaned or cleaned == st.session_state.query_signature:
        return

    st.session_state.query_signature = cleaned
    result = st.session_state.intent_agent.parse(cleaned)
    if not result.success or not result.criteria:
        return

    criteria = result.criteria
    st.session_state.filters = {
        "origin": criteria.origin,
        "destination": criteria.destination,
        "depart": criteria.depart_date,
        "return_enabled": bool(criteria.return_date),
        "return_date": criteria.return_date or date.today(),
        "cabin": criteria.cabin,
        "adults": criteria.adults,
        "max_results": criteria.max_results,
        "price_cap": criteria.price_cap or 0.0,
    }
    st.session_state.origin_filter = criteria.origin
    st.session_state.destination_filter = criteria.destination
    st.session_state.depart_filter = criteria.depart_date
    st.session_state.return_filter = bool(criteria.return_date)
    st.session_state.return_date_filter = criteria.return_date or date.today()
    st.session_state.cabin_filter = criteria.cabin
    st.session_state.adults_filter = criteria.adults
    st.session_state.price_filter = criteria.price_cap or 0.0


def _weather_card(point) -> str:
    if not point:
        return (
            '<div class="weather-card"><h4>Weather unavailable</h4>'
            '<div class="weather-meta">No airport forecast was returned.</div></div>'
        )
    temperature = (
        f"{point.temperature_c:.0f}°C" if point.temperature_c is not None else "—"
    )
    wind = (
        f"{point.wind_speed_kph:.0f} km/h wind"
        if point.wind_speed_kph is not None
        else "Wind unavailable"
    )
    return f"""
        <div class="weather-card">
            <h4>{escape(point.code)} · {escape(point.name or "Airport")}</h4>
            <div class="weather-temp">{temperature}</div>
            <div class="weather-meta">{wind}</div>
        </div>
    """


def _render_itinerary(itinerary) -> None:
    segment = itinerary.segments[0]
    duration_hours, duration_minutes = divmod(segment.duration_minutes, 60)
    duration = f"{duration_hours}h {duration_minutes}m"
    st.markdown(
        f"""
        <div class="itinerary-card">
            <div style="display:flex;justify-content:space-between;gap:1rem">
                <div>
                    <div class="flight-number">{escape(segment.marketing_carrier)} ·
                        {escape(segment.flight_number)} · {escape(segment.cabin)}</div>
                    <div class="route">{escape(segment.origin)} → {escape(segment.destination)}</div>
                    <div class="flight-meta">{segment.depart_time:%a, %b %d} ·
                        {segment.depart_time:%H:%M} – {segment.arrive_time:%H:%M} ·
                        {duration}</div>
                </div>
                <div>
                    <div class="price-label">Total fare</div>
                    <div class="price">{itinerary.fare.currency} {itinerary.fare.total:,.2f}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_initialise_state()

st.markdown(
    """
    <div class="hero">
        <h1>✈️ Find your next flight</h1>
        <p>Describe your trip in plain language and we’ll tailor the search for you.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

query = st.text_input(
    "Trip request",
    placeholder="Try: Round trip from SFO to JFK next Friday in business under $600",
    label_visibility="collapsed",
)
_apply_natural_language_query(query)

filters = st.session_state.filters
st.markdown('<div class="section-title">Search preferences</div>', unsafe_allow_html=True)
with st.container(border=True):
    row_one = st.columns(4)
    with row_one[0]:
        origin = st.text_input("From", value=filters["origin"], key="origin_filter")
    with row_one[1]:
        destination = st.text_input(
            "To", value=filters["destination"], key="destination_filter"
        )
    with row_one[2]:
        depart = st.date_input("Departure", value=filters["depart"], key="depart_filter")
    with row_one[3]:
        cabin_options = ["ECONOMY", "PREMIUM", "BUSINESS"]
        cabin = st.selectbox(
            "Cabin",
            cabin_options,
            index=cabin_options.index(filters["cabin"])
            if filters["cabin"] in cabin_options
            else 0,
            key="cabin_filter",
        )

    row_two = st.columns(4)
    with row_two[0]:
        return_enabled = st.checkbox(
            "Round trip", value=filters["return_enabled"], key="return_filter"
        )
    with row_two[1]:
        return_date = (
            st.date_input(
                "Return",
                value=filters["return_date"],
                disabled=not return_enabled,
                key="return_date_filter",
            )
            if return_enabled
            else None
        )
    with row_two[2]:
        adults = st.number_input(
            "Travellers", min_value=1, max_value=9, value=filters["adults"], key="adults_filter"
        )
    with row_two[3]:
        price_cap_input = st.number_input(
            "Max fare (USD)", min_value=0.0, value=float(filters["price_cap"] or 0.0),
            step=50.0, key="price_filter",
        )

criteria = SearchCriteria(
    origin=origin,
    destination=destination,
    depart_date=depart,
    return_date=return_date,
    cabin=cabin,
    adults=adults,
    max_results=filters["max_results"],
    price_cap=price_cap_input or None,
)

st.markdown('<div class="section-title">Available flights</div>', unsafe_allow_html=True)
search_col, weather_col = st.columns([1, 5])
with search_col:
    search_flights = st.button("Search flights", type="primary", use_container_width=True)
with weather_col:
    include_weather = st.checkbox("Include destination weather", value=True)

if search_flights:
    plan = st.session_state.orchestrator.build_plan(
        "Search flights", include_return=bool(return_date), mode="search",
        include_weather=include_weather,
    )
    result = st.session_state.orchestrator.execute(
        plan=plan, criteria=criteria, passengers=[], selected_itinerary_id=None,
        payment_card_token=None, preloaded_itineraries=None,
    )
    st.session_state.itineraries = result["context"]["itineraries"]
    st.session_state.weather_report = result["context"]["weather"]
    st.session_state.selected_itinerary_id = (
        st.session_state.itineraries[0].id if st.session_state.itineraries else None
    )

if st.session_state.weather_report:
    report = st.session_state.weather_report
    st.markdown('<div class="section-title">Current conditions</div>', unsafe_allow_html=True)
    weather_columns = st.columns(2)
    with weather_columns[0]:
        st.markdown(_weather_card(report.origin), unsafe_allow_html=True)
    with weather_columns[1]:
        st.markdown(_weather_card(report.destination), unsafe_allow_html=True)
    st.caption(f"Updated {report.fetched_at:%b %d, %Y at %H:%M} · {report.provider}")

itineraries = st.session_state.itineraries
if itineraries:
    st.session_state.setdefault("selected_itinerary_id", itineraries[0].id)
    for start in range(0, len(itineraries), 2):
        itinerary_columns = st.columns(2)
        for column, itinerary in zip(itinerary_columns, itineraries[start : start + 2]):
            with column:
                _render_itinerary(itinerary)
                if st.button(
                    "Selected" if st.session_state.selected_itinerary_id == itinerary.id else "Select flight",
                    key=f"select_{itinerary.id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_itinerary_id = itinerary.id
                    st.rerun()
    selected_id = st.session_state.selected_itinerary_id
else:
    selected_id = None
    st.info("Enter a trip request and search to see available flights.")

st.markdown('<div class="section-title">Passenger details</div>', unsafe_allow_html=True)
passenger_columns = st.columns(2)
with passenger_columns[0]:
    pax_first = st.text_input("First name", "John")
with passenger_columns[1]:
    pax_last = st.text_input("Last name", "Doe")
card_token = st.text_input("Payment token", "tok_visa_4242", type="password")

if st.button("Complete booking", use_container_width=True):
    if not itineraries:
        st.error("Search for a flight before completing your booking.")
    elif not selected_id:
        st.error("Choose an itinerary first.")
    else:
        passengers: List[Passenger] = [
            Passenger(first_name=pax_first, last_name=pax_last)
        ]
        plan = st.session_state.orchestrator.build_plan(
            "Book selected itinerary", include_return=bool(return_date),
            mode="book", include_weather=False,
        )
        result = st.session_state.orchestrator.execute(
            plan=plan, criteria=criteria, passengers=passengers,
            selected_itinerary_id=selected_id, payment_card_token=card_token,
            preloaded_itineraries=itineraries,
        )
        final = result["final"]
        (st.success if "completed" in final.answer.lower() else st.error)(final.answer)
        if final.key_points:
            st.markdown("**Booking details**")
            for key_point in final.key_points:
                st.markdown(f"- {key_point}")
