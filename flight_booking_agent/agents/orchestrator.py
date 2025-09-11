from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime
import uuid

from agent_models import (
    OrchestratorPlan, PlanStep, StepResult, SearchCriteria, Passenger,
    BookingRequest, PaymentRequest, FinalAnswer
)
from agents.flight_search_agent import FlightSearchAgent
from agents.pricing_agent import PricingAgent
from agents.booking_agent import BookingAgent
from agents.payment_agent import PaymentAgent
from agents.ticketing_agent import TicketingAgent

class OrchestratorAgent:
    def __init__(self):
        self.flight_search = FlightSearchAgent()
        self.pricing = PricingAgent()
        self.booking = BookingAgent()
        self.payment = PaymentAgent()
        self.ticketing = TicketingAgent()

    def build_plan(self, intent: str, include_return: bool) -> OrchestratorPlan:
        steps = [
            PlanStep(step_id=1, name="search_flights", agent="flight_search_agent", action="search",
                     description="Search inventory", args={}),
            PlanStep(step_id=2, name="price_itineraries", agent="pricing_agent", action="reprice",
                     description="Reprice / normalize fares", args={}),
            PlanStep(step_id=3, name="create_booking", agent="booking_agent", action="create_booking",
                     description="Hold booking seats", args={}),
            PlanStep(step_id=4, name="authorize_payment", agent="payment_agent", action="authorize",
                     description="Authorize & capture payment", args={}),
            PlanStep(step_id=5, name="issue_ticket", agent="ticketing_agent", action="issue",
                     description="Issue e-tickets", args={}),
        ]
        return OrchestratorPlan(intent=intent, steps=steps)

    def execute(
        self,
        plan: OrchestratorPlan,
        criteria: SearchCriteria,
        passengers: List[Passenger],
        selected_itinerary_id: str | None,
        payment_card_token: str | None
    ) -> Dict[str, Any]:
        results: List[StepResult] = []
        context: Dict[str, Any] = {
            "itineraries": [],
            "selected": None,
            "booking": None,
            "payment": None,
            "tickets": None
        }
        for step in plan.steps:
            start = datetime.utcnow()
            success = True
            output = None
            error = None
            try:
                if step.name == "search_flights":
                    itins = self.flight_search.search(criteria)
                    context["itineraries"] = itins
                    output = f"{len(itins)} itineraries found."
                elif step.name == "price_itineraries":
                    context["itineraries"] = self.pricing.reprice(context["itineraries"])
                    output = "Pricing refreshed."
                elif step.name == "create_booking":
                    if not selected_itinerary_id:
                        raise ValueError("No itinerary selected.")
                    itin = next((i for i in context["itineraries"] if i.id == selected_itinerary_id), None)
                    if not itin:
                        raise ValueError("Selected itinerary not found.")
                    context["selected"] = itin
                    booking_req = BookingRequest(
                        itinerary_id=itin.id,
                        passengers=passengers,
                        client_reference=str(uuid.uuid4())[:12]
                    )
                    booking = self.booking.create_booking(booking_req, itin, passengers)
                    context["booking"] = booking
                    output = f"Booking held: {booking.booking_id}"
                elif step.name == "authorize_payment":
                    if not context["booking"]:
                        raise ValueError("No booking to pay.")
                    if not payment_card_token:
                        raise ValueError("Missing card token.")
                    amount = context["booking"].itinerary.fare.total
                    pay_req = PaymentRequest(
                        booking_id=context["booking"].booking_id,
                        amount=amount,
                        currency="USD",
                        card_token=payment_card_token,
                        capture=True,
                        idempotency_key=str(uuid.uuid4())
                    )
                    pay_res = self.payment.authorize(pay_req)
                    context["payment"] = pay_res
                    if pay_res.status != "CAPTURED":
                        raise ValueError("Payment failed.")
                    output = f"Payment {pay_res.status} amount={pay_res.authorized_amount}"
                elif step.name == "issue_ticket":
                    if not context["booking"] or not context["payment"]:
                        raise ValueError("Booking or payment missing.")
                    tickets = self.ticketing.issue(context["booking"], context["payment"])
                    context["tickets"] = tickets
                    output = f"Issued {len(tickets.ticket_numbers)} tickets."
                else:
                    success = False
                    error = f"Unknown step {step.name}"
            except Exception as e:
                success = False
                error = str(e)
            end = datetime.utcnow()
            results.append(
                StepResult(
                    step_id=step.step_id,
                    name=step.name,
                    success=success,
                    output=output,
                    error=error,
                    started_at=start,
                    ended_at=end
                )
            )
            if not success:
                break

        # Construct summary FinalAnswer
        failures = [r for r in results if not r.success]
        if failures:
            answer_text = f"Workflow stopped at step {failures[0].name}: {failures[0].error}"
            key_points = [f"Completed {len([r for r in results if r.success])} steps successfully."]
            followups = ["Adjust selection or payment details and retry."]
        else:
            answer_text = "Booking completed successfully; tickets issued."
            key_points = [
                f"Itineraries searched: {len(context['itineraries'])}",
                f"Booking ID: {context['booking'].booking_id if context['booking'] else 'N/A'}",
                f"Tickets: {', '.join(context['tickets'].ticket_numbers) if context['tickets'] else 'N/A'}"
            ]
            followups = [
                "Would you like to add travel insurance?",
                "Need to select seats or add baggage?",
                "Should I email or download the itinerary PDF?"
            ]
        final = FinalAnswer(answer=answer_text, key_points=key_points, follow_up_questions=followups)
        return {
            "plan": plan,
            "steps": results,
            "context": context,
            "final": final
        }