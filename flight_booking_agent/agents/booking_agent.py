from __future__ import annotations
from typing import List
from agent_models import BookingRequest, BookingRecord, Passenger, Itinerary
from agent_tools import hold_booking

class BookingAgent:
    name = "booking_agent"

    def create_booking(self, req: BookingRequest, itinerary: Itinerary, passengers: List[Passenger]) -> BookingRecord:
        return hold_booking(req, itinerary, passengers)