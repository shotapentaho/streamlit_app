import streamlit as st
from datetime import date
from typing import List

from agent_models import SearchCriteria, Passenger, IntentParseResult
from agents.orchestrator import OrchestratorAgent
from agents.intent_agent import IntentAgent
from secrets_loader import resolve_openai_api_key  # NEW

st.set_page_config(page_title="Flight Booking Agent", page_icon="✈️", layout="wide")
st.title("✈️ Flight Ticket Booking (Agentic Prototype + Intent + Weather)")

# --- Resolve OpenAI API key via secrets (.streamlit/secrets.toml) ---
api_key = resolve_openai_api_key(set_env=True)
if api_key:
    st.sidebar.success("OpenAI key loaded.")
else:
    st.sidebar.warning("No OpenAI key found (secrets.toml or env). Intent parsing will use heuristics.")

# Session state init
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = OrchestratorAgent()
if "itineraries" not in st.session_state:
    st.session_state.itineraries = []
if "weather_report" not in st.session_state:
    st.session_state.weather_report = None
if "parsed_intent" not in st.session_state:
    st.session_state.parsed_intent: IntentParseResult | None = None
if "intent_agent" not in st.session_state:
    st.session_state.intent_agent = IntentAgent(api_key=api_key)  # inject key once

# --- Natural Language Intent Section ---
st.subheader("0. Natural Language Request")
nl_query = st.text_input(
    "Describe your trip (e.g. 'Need a round trip SFO to JFK next week in business under $600')",
    value=""
)
col_intent_a, col_intent_b = st.columns([1, 1])
with col_intent_a:
    if st.button("Parse Intent"):
        result = st.session_state.intent_agent.parse(nl_query or "Round trip SFO to JFK next week")
        st.session_state.parsed_intent = result
        if result.success and result.criteria:
            st.success("Intent parsed.")
        else:
            st.error("Failed to parse intent.")
with col_intent_b:
    if st.button("Apply Parsed Criteria") and st.session_state.parsed_intent and st.session_state.parsed_intent.criteria:
        crit = st.session_state.parsed_intent.criteria
        st.session_state._origin = crit.origin
        st.session_state._destination = crit.destination
        st.session_state._depart = crit.depart_date
        st.session_state._return_enabled = bool(crit.return_date)
        st.session_state._return_date = crit.return_date or date.today()
        st.session_state._cabin = crit.cabin
        st.session_state._adults = crit.adults
        st.session_state._max_results = crit.max_results
        st.session_state._price_cap = crit.price_cap
        st.success("Criteria applied to UI controls (adjust below if needed).")

if st.session_state.parsed_intent:
    with st.expander("Parsed Intent JSON", expanded=False):
        st.json(st.session_state.parsed_intent.model_dump())

# --- Structured Criteria Inputs ---
st.subheader("1. Search Criteria (Structured)")

def ss_get(key, default):
    return st.session_state.get(key, default)

origin = st.text_input("Origin (IATA)", ss_get("_origin", "SFO"))
destination = st.text_input("Destination (IATA)", ss_get("_destination", "JFK"))
depart = st.date_input("Departure Date", value=ss_get("_depart", date.today()))
return_enabled = st.checkbox("Return Trip?", value=ss_get("_return_enabled", False))
return_date = st.date_input("Return Date", value=ss_get("_return_date", date.today())) if return_enabled else None
cabin = st.selectbox("Cabin", ["ECONOMY", "PREMIUM", "BUSINESS"], index=["ECONOMY", "PREMIUM", "BUSINESS"].index(ss_get("_cabin", "ECONOMY")))
adults = st.number_input("Adults", min_value=1, max_value=9, value=ss_get("_adults", 1))
max_results = st.slider("Max Results", 1, 20, ss_get("_max_results", 6))
price_cap_val = float(ss_get("_price_cap", 0.0) or 0.0)
price_cap = st.number_input("Optional Price Cap (USD)", min_value=0.0, value=price_cap_val, step=50.0)
if price_cap == 0:
    price_cap = None

include_weather = st.checkbox("Include Weather in Search Flow", value=True)

criteria = SearchCriteria(
    origin=origin,
    destination=destination,
    depart_date=depart,
    return_date=return_date,
    cabin=cabin,
    adults=adults,
    max_results=max_results,
    price_cap=price_cap
)

st.subheader("2. Search & Select Itinerary")

if st.button("Search / Refresh"):
    plan = st.session_state.orchestrator.build_plan(
        "Search flights",
        include_return=bool(return_date),
        mode="search",
        include_weather=include_weather
    )
    result = st.session_state.orchestrator.execute(
        plan=plan,
        criteria=criteria,
        passengers=[],
        selected_itinerary_id=None,
        payment_card_token=None,
        preloaded_itineraries=None
    )
    st.session_state.itineraries = result["context"]["itineraries"]
    st.session_state.weather_report = result["context"]["weather"]
    st.success(f"Loaded {len(st.session_state.itineraries)} itineraries.")

if st.session_state.weather_report:
    wr = st.session_state.weather_report
    with st.expander("Weather", expanded=True):
        if wr.origin:
            st.markdown(f"Origin {wr.origin.code}: {wr.origin.temperature_c}°C wind {wr.origin.wind_speed_kph} km/h")
        if wr.destination:
            st.markdown(f"Destination {wr.destination.code}: {wr.destination.temperature_c}°C wind {wr.destination.wind_speed_kph} km/h")
        st.caption(f"Fetched at: {wr.fetched_at}")

selected_id = st.selectbox(
    "Select Itinerary",
    [i.id for i in st.session_state.itineraries] or ["(none)"]
)

if st.session_state.itineraries and selected_id != "(none)":
    chosen = next((i for i in st.session_state.itineraries if i.id == selected_id), None)
    if chosen:
        seg = chosen.segments[0]
        st.write(f"Price: {chosen.fare.total:.2f} {chosen.fare.currency}")
        st.write(f"{seg.marketing_carrier}{seg.flight_number} {seg.origin}->{seg.destination}")
        st.write(f"Depart: {seg.depart_time} | Arrive: {seg.arrive_time} | {seg.duration_minutes} mins")

st.subheader("3. Passenger & Payment")
pax_first = st.text_input("Passenger First Name", "John")
pax_last = st.text_input("Passenger Last Name", "Doe")
card_token = st.text_input("Card Token (fake)", "tok_visa_4242")

st.subheader("4. Orchestrate Booking")
if st.button("Complete Booking"):
    if not st.session_state.itineraries:
        st.error("No itineraries loaded. Run a search first.")
    elif selected_id == "(none)":
        st.error("Select an itinerary first.")
    else:
        passengers: List[Passenger] = [Passenger(first_name=pax_first, last_name=pax_last)]
        plan = st.session_state.orchestrator.build_plan(
            "Book selected itinerary",
            include_return=bool(return_date),
            mode="book",
            include_weather=False
        )
        result = st.session_state.orchestrator.execute(
            plan=plan,
            criteria=criteria,
            passengers=passengers,
            selected_itinerary_id=selected_id,
            payment_card_token=card_token,
            preloaded_itineraries=st.session_state.itineraries
        )
        final = result["final"]
        (st.success if "completed" in final.answer.lower() else st.error)(final.answer)

        st.markdown("**Key Points**")
        for kp in final.key_points:
            st.markdown(f"- {kp}")

        st.markdown("**Follow-ups**")
        for fq in final.follow_up_questions:
            st.markdown(f"- {fq}")

        st.markdown("**Step Log**")
        for step in result["steps"]:
            with st.expander(f"Step {step.step_id}: {step.name}", expanded=True):
                st.write(f"Success: {step.success}")
                if step.output:
                    st.write(f"Output: {step.output}")
                if step.error:
                    st.error(step.error)

st.markdown("---")
st.caption("Agentic Flight Booking • Secrets loaded via .streamlit/secrets.toml (precedence over env).")