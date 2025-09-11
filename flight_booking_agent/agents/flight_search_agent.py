from __future__ import annotations
from typing import List
from agent_models import SearchCriteria, Itinerary
from agent_tools import generate_mock_itineraries

class FlightSearchAgent:
    name = "flight_search_agent"

    def search(self, criteria: SearchCriteria) -> List[Itinerary]:
        return generate_mock_itineraries(criteria)