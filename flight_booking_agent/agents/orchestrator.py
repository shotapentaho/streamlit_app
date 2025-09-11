from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from agent_models import (
    OrchestratorPlan, PlanStep, StepResult, SearchCriteria, Passenger,
    BookingRequest, PaymentRequest, FinalAnswer, WeatherReport
)
from agent_models import Itinerary  # for typing
from agents.flight_search_agent import FlightSearchAgent
from agents.pricing_agent import PricingAgent
from agents.booking_agent import BookingAgent
from agents.payment_agent import PaymentAgent
from agents.ticketing_agent import TicketingAgent
from agents.weather_agent import WeatherAgent

class OrchestratorAgent:
    """
    Coordinates multi-step flight booking workflow.
    Adds optional weather step.
    """

    def __init__(self):
        self.flight_search = FlightSearchAgent()
        self.pricing = PricingAgent()
        self.booking = BookingAgent()
        self.payment = PaymentAgent()
        self.ticketing = TicketingAgent()
        self.weather = WeatherAgent()

    def build_plan(self, intent: str, include_return: bool, mode: str = "full", include_weather: bool = False) -> OrchestratorPlan:
        """
        mode:
          - 'search': only search + pricing [+ weather if requested]
          - 'book': booking onward
          - 'full': entire pipeline
        """
        steps: List[PlanStep] = []
        if mode in ("search", "full"):
            steps.append(PlanStep(step_id=len(steps)+1, name="search_flights", agent="flight_search_agent",
                                  action="search", description="Search inventory", args={}))
            steps.append(PlanStep(step_id=len(steps)+1, name="price_itineraries", agent="pricing_agent",
                                  action="reprice", description="Reprice / normalize fares", args={}))
            if include_weather:
                steps.append(PlanStep(step_id=len(steps)+1, name="get_weather", agent="weather_agent",
                                      action="get_report", description="Fetch origin/destination weather", args={}))

        if mode in ("book", "full"):
            steps.append(PlanStep(step_id=len(steps)+1, name="create_booking", agent="booking_agent",
                                  action="create_booking", description="Hold booking seats", args={}))
            steps.append(PlanStep(step_id=len(steps)+1, name="authorize_payment", agent="payment_agent",
                                  action="authorize", description="Authorize & capture payment", args={}))
            steps.append(PlanStep(step_id=len(steps)+1, name="issue_ticket", agent="ticketing_agent",
                                  action="issue", description="Issue e-tickets", args={}))

        return OrchestratorPlan(intent=intent, steps=steps)

    def execute(
        self,
        plan: OrchestratorPlan,
        criteria: SearchCriteria,
        passengers: List[Passenger],
        selected_itinerary_id: Optional[str],
        payment_card_token: Optional[str],
        preloaded_itineraries: Optional[List[Itinerary]] = None
    ) -> Dict[str, Any]:
        results: List[StepResult] = []
        context: Dict[str, Any] = {
            "itineraries": preloaded_itineraries[:] if preloaded_itineraries else [],
            "selected": None,
            "booking": None,
            "payment": None,
            "tickets": None,
            "weather": None
        }

        for step in plan.steps:
            start = datetime.utcnow()
            success = True
            output = None
            error = None

            try:
                if step.name == "search_flights":
                    if context["itineraries"]:
                        output = f"Skipped search; using {len(context['itineraries'])} preloaded itineraries."
                    else:
                        itins = self.flight_search.search(criteria)
                        # Optional price cap filtering later in pricing step; here we just store
                        context["itineraries"] = itins
                        output = f"{len(itins)} itineraries found."
                elif step.name == "price_itineraries":
                    if not context["itineraries"]:
                        raise ValueError("No itineraries to price.")
                    context["itineraries"] = self.pricing.reprice(context["itineraries"])
                    # Apply price cap filter if present
                    if criteria.price_cap:
                        before = len(context["itineraries"])
                        context["itineraries"] = [
                            i for i in context["itineraries"] if i.fare.total <= criteria.price_cap
                        ]
                        output = f"Pricing refreshed. Filtered {before}->{len(context['itineraries'])} by price_cap."
                    else:
                        output = "Pricing refreshed."
                elif step.name == "get_weather":
                    report: WeatherReport = self.weather.get_report(criteria.origin, criteria.destination)
                    context["weather"] = report
                    if report.origin and report.destination:
                        output = (f"Weather O:{report.origin.temperature_c}C D:{report.destination.temperature_c}C")
                    else:
                        output = "Weather partial or unavailable."
                elif step.name == "create_booking":
                    if not selected_itinerary_id:
                        raise ValueError("No itinerary selected.")
                    if not context["itineraries"]:
                        raise ValueError("Itinerary list empty; cannot match selection.")
                    itin = next((i for i in context["itineraries"] if i.id == selected_itinerary_id), None)
                    if not itin:
                        raise ValueError("Selected itinerary not found in current list.")
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
                        raise ValueError("Missing payment card token.")
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

        failures = [r for r in results if not r.success]
        if failures:
            answer_text = f"Workflow stopped at step {failures[0].name}: {failures[0].error}"
            key_points = [f"Successful steps: {len([r for r in results if r.success])}"]
            followups = ["Adjust selection or input and retry.", "Check payment token."]
        else:
            answer_text = "Workflow completed."
            key_points = [
                f"Itineraries: {len(context['itineraries'])}",
                f"Selected: {context['selected'].id if context['selected'] else 'N/A'}",
                f"Booking: {context['booking'].booking_id if context['booking'] else 'N/A'}",
                f"Tickets: {', '.join(context['tickets'].ticket_numbers) if context['tickets'] else 'N/A'}"
            ]
            if context.get("weather"):
                w = context["weather"]
                if w.origin and w.destination and w.origin.temperature_c is not None:
                    key_points.append(f"Origin temp {w.origin.code}: {w.origin.temperature_c}C")
                if w.destination and w.destination.temperature_c is not None:
                    key_points.append(f"Dest temp {w.destination.code}: {w.destination.temperature_c}C")
            followups = [
                "Add seat selection?",
                "Need fare rules details?",
                "Send itinerary via email?"
            ]

        final = FinalAnswer(answer=answer_text, key_points=key_points, follow_up_questions=followups)
        return {
            "plan": plan,
            "steps": results,
            "context": context,
            "final": final
        }