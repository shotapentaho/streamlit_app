from __future__ import annotations
from datetime import datetime
from typing import List
from agent_models import Itinerary, FareComponent

class PricingAgent:
    name = "pricing_agent"

    def reprice(self, itineraries: List[Itinerary]) -> List[Itinerary]:
        # Stub: maybe add dynamic margin or discounts
        updated = []
        for itin in itineraries:
            fare = itin.fare
            # Example: add surcharge or adjust taxes
            adjusted_taxes = round(fare.taxes * 1.0, 2)
            new_fare = FareComponent(
                base_fare=fare.base_fare,
                taxes=adjusted_taxes,
                currency=fare.currency,
                baggage_allowance=fare.baggage_allowance,
                refundable=fare.refundable,
                fare_basis=fare.fare_basis or "YBASIC"
            )
            itin.fare = new_fare
            itin.pricing_timestamp = datetime.utcnow()
            updated.append(itin)
        return updated