from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import uuid

from agent_models import (
    SearchCriteria,
    FlightSegment,
    FareComponent,
    Itinerary,
    Passenger,
    BookingRequest,
    BookingRecord,
    PaymentRequest,
    PaymentResult,
    TicketRecord
)

# Utility & Tool Functions used by Agents (pure / deterministic stubs)

AIRLINES = ["AV", "UA", "AA", "DL", "LH", "BA"]
EQUIPMENT = ["320", "321", "738", "739", "789", "332", "223"]

def generate_mock_itineraries(criteria: SearchCriteria) -> List[Itinerary]:
    """Stub flight search."""
    itineraries: List[Itinerary] = []
    for i in range(min(criteria.max_results, 6)):
        dep_hour = random.randint(6, 20)
        dep = datetime.combine(criteria.depart_date, datetime.min.time()) + timedelta(hours=dep_hour)
        duration = random.randint(90, 360)
        arr = dep + timedelta(minutes=duration)
        seg = FlightSegment(
            marketing_carrier=random.choice(AIRLINES),
            flight_number=str(random.randint(100, 9999)),
            origin=criteria.origin,
            destination=criteria.destination,
            depart_time=dep,
            arrive_time=arr,
            duration_minutes=duration,
            cabin=criteria.cabin,
            equipment=random.choice(EQUIPMENT)
        )
        base = round(random.uniform(80, 550), 2)
        taxes = round(base * random.uniform(0.08, 0.25), 2)
        fare = FareComponent(base_fare=base, taxes=taxes, currency="USD", baggage_allowance="1PC", refundable=bool(random.getrandbits(1)))
        itineraries.append(
            Itinerary(
                id=str(uuid.uuid4())[:8],
                segments=[seg],
                fare=fare,
                pricing_timestamp=datetime.utcnow(),
                score=round(random.uniform(0, 1), 3),
                meta={"stops": 0}
            )
        )
    return itineraries


def repr_price(itin: Itinerary) -> str:
    return f"{itin.fare.total:.2f} {itin.fare.currency}"


def hold_booking(req: BookingRequest, itinerary: Itinerary, passengers: List[Passenger]) -> BookingRecord:
    return BookingRecord(
        booking_id="BK" + str(uuid.uuid4())[:10],
        itinerary=itinerary,
        passengers=passengers,
        created_at=datetime.utcnow(),
        status="HELD",
        hold_expires_at=datetime.utcnow() + timedelta(minutes=15)
    )


def authorize_payment(pr: PaymentRequest) -> PaymentResult:
    approved = random.random() > 0.05
    return PaymentResult(
        payment_id="PMT" + str(uuid.uuid4())[:10],
        booking_id=pr.booking_id,
        authorized_amount=pr.amount if approved else 0.0,
        currency=pr.currency,
        status="CAPTURED" if approved else "FAILED",
        processor_ref="SIMPROC-" + str(uuid.uuid4())[:6],
        created_at=datetime.utcnow()
    )


def issue_tickets(booking: BookingRecord, payment: PaymentResult) -> TicketRecord:
    nums = ["ET" + str(random.randint(1000000000, 9999999999)) for _ in booking.passengers]
    return TicketRecord(
        ticket_numbers=nums,
        booking_id=booking.booking_id,
        issued_at=datetime.utcnow(),
        status="ISSUED"
    )