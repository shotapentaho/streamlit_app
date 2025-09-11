import streamlit as st
from datetime import date
from typing import List
from agent_models import SearchCriteria, Passenger
from agents.orchestrator import OrchestratorAgent

st.set_page_config(page_title="Flight Booking Agent", page_icon="✈️", layout="wide")
st.title("✈️ Flight Ticket Booking (Agentic Prototype)")

# Maintain orchestrator & itineraries in session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = OrchestratorAgent()
if "itineraries" not in st.session_state:
    st.session_state.itineraries = []

with st.sidebar:
    st.header("Search Criteria")
    origin = st.text_input("Origin (IATA)", "SFO")
    destination = st.text_input("Destination (IATA)", "JFK")
    depart = st.date_input("Departure Date", value=date.today())
    ret_en = st.checkbox("Return Trip?", value=False)
    ret_date = st.date_input("Return Date", value=date.today()) if ret_en else None
    cabin = st.selectbox("Cabin", ["ECONOMY", "PREMIUM", "BUSINESS"])
    adults = st.number_input("Adults", min_value=1, max_value=9, value=1)
    max_results = st.slider("Max Results", 1, 20, 6)
    st.markdown("---")
    st.caption("Prototype - not real airline data.")

criteria = SearchCriteria(
    origin=origin,
    destination=destination,
    depart_date=depart,
    return_date=ret_date,
    cabin=cabin,
    adults=adults,
    max_results=max_results
)

st.subheader("1. Search & Select Itinerary")

if st.button("Search Flights / Refresh"):
    # Build a 'search' mode plan (only search + price)
    plan = st.session_state.orchestrator.build_plan("Search flights", include_return=ret_en, mode="search")
    result = st.session_state.orchestrator.execute(
        plan=plan,
        criteria=criteria,
        passengers=[],  # none yet
        selected_itinerary_id=None,
        payment_card_token=None,
        preloaded_itineraries=None  # force new search
    )
    st.session_state.itineraries = result["context"]["itineraries"]
    st.success(f"Loaded {len(st.session_state.itineraries)} itineraries.")

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

st.subheader("2. Passenger & Payment")
pax_first = st.text_input("Passenger First Name", "John")
pax_last = st.text_input("Passenger Last Name", "Doe")
card_token = st.text_input("Card Token (fake)", "tok_visa_4242")

st.subheader("3. Orchestrate Booking")
if st.button("Complete Booking"):
    if not st.session_state.itineraries:
        st.error("No itineraries loaded. Run a search first.")
    elif selected_id == "(none)":
        st.error("Select an itinerary first.")
    else:
        passengers: List[Passenger] = [Passenger(first_name=pax_first, last_name=pax_last)]
        # Build a 'book' mode plan (skip search/pricing)
        plan = st.session_state.orchestrator.build_plan("Book selected itinerary", include_return=ret_en, mode="book")
        result = st.session_state.orchestrator.execute(
            plan=plan,
            criteria=criteria,
            passengers=passengers,
            selected_itinerary_id=selected_id,
            payment_card_token=card_token,
            preloaded_itineraries=st.session_state.itineraries  # reuse existing
        )
        final = result["final"]
        if "successfully" in final.answer.lower():
            st.success(final.answer)
        else:
            st.error(final.answer)

        st.markdown("**Key Points**")
        for kp in final.key_points:
            st.markdown(f"- {kp}")

        st.markdown("**Follow-ups**")
        for fq in final.follow_up_questions:
            st.markdown(f"- {fq}")

        st.markdown("**Step Log**")
        for step in result["steps"]:
            color = "green" if step.success else "red"
            with st.expander(f"Step {step.step_id}: {step.name}", expanded=True):
                st.write(f"Status: :{color}[{'SUCCESS' if step.success else 'FAILED'}]")
                st.write(f"Output: {step.output}")
                if step.error:
                    st.error(step.error)

st.markdown("---")
st.caption("Agentic Flight Booking Prototype • IDs preserved across booking by reusing preloaded itineraries.")