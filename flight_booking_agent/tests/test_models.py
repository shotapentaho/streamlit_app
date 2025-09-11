from datetime import date, datetime
from agent_models import SearchCriteria, FlightSegment, FareComponent, Itinerary, FinalAnswer

def test_search_criteria_upper():
    sc = SearchCriteria(origin="sfo", destination="jfk", depart_date=date.today())
    assert sc.origin == "SFO"
    assert sc.destination == "JFK"

def test_itinerary_total():
    seg = FlightSegment(
        marketing_carrier="AA",
        flight_number="100",
        origin="SFO",
        destination="JFK",
        depart_time=datetime.utcnow(),
        arrive_time=datetime.utcnow(),
        duration_minutes=300,
        cabin="ECONOMY"
    )
    fare = FareComponent(base_fare=100, taxes=25, currency="USD")
    itin = Itinerary(id="X1", segments=[seg], fare=fare, pricing_timestamp=datetime.utcnow())
    assert itin.fare.total == 125

def test_final_answer_coercion():
    fa = FinalAnswer(answer={"insights": "done"}, key_points="Point A", follow_up_questions=None)
    assert isinstance(fa.answer, str)
    assert fa.key_points == ["Point A"]