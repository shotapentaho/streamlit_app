# Flight Booking Agentic Prototype (Streamlit + Multi-Agent Orchestration)

This is a reference architecture & scaffold for a flight ticket booking system using an **agentic pattern**:
- Streamlit UI
- Orchestrator Agent (plans + executes steps)
- Specialized sub-agents: FlightSearch, Pricing, Booking, Payment, Ticketing
- Pydantic models for strong typing, validation, and composability

## Why Agentic?
- Separation of concerns (search vs pricing vs booking)
- Extensible: add LoyaltyAgent, DisruptionAgent later
- Transparency: each step logged with inputs/outputs
- Robust final answer coercion (no validation crashes when upstream returns dicts)

## Quick Start
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Flow
1. User defines search criteria.
2. Orchestrator builds plan (search → price → booking → payment → ticket).
3. User selects itinerary.
4. Orchestrator executes full plan and shows step log + final summary.

## Extending
- Replace `generate_mock_itineraries` with real GDS/NDC API calls.
- Implement proper pricing rules, taxes, ancillaries.
- Integrate a PCI-compliant payment gateway (never store raw card data).
- Add notification/email microservice for itinerary delivery.

## Security & Compliance (Future)
- Secrets via environment or secret manager.
- Strict logging (no PAN, no PII beyond minimal).
- Add rate limiting, audit trail, and SSO if productionized.

## Tests
Basic tests in `tests/test_models.py` for model sanity and FinalAnswer coercion.

## Disclaimer
All external calls are stubbed; do not use in production without implementing real services, compliance, and security layers.