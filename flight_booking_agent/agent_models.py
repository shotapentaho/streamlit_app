# v15 — Added IntentParseResult & WeatherReport for intent + weather integration
from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

# ---------- Core Search / Flight Structures ----------

class SearchCriteria(BaseModel):
    origin: str
    destination: str
    depart_date: date
    return_date: Optional[date] = None
    cabin: str = "ECONOMY"
    adults: int = 1
    max_results: int = 20
    price_cap: Optional[float] = None

    @field_validator("origin", "destination")
    @classmethod
    def upper_iata(cls, v: str) -> str:
        return v.strip().upper()


class FlightSegment(BaseModel):
    marketing_carrier: str
    flight_number: str
    origin: str
    destination: str
    depart_time: datetime
    arrive_time: datetime
    duration_minutes: int
    cabin: str
    equipment: Optional[str] = None


class FareComponent(BaseModel):
    base_fare: float
    taxes: float
    currency: str = "USD"
    baggage_allowance: Optional[str] = None
    refundable: bool = False
    fare_basis: Optional[str] = None

    @property
    def total(self) -> float:
        return round(self.base_fare + self.taxes, 2)


class Itinerary(BaseModel):
    id: str
    segments: List[FlightSegment]
    fare: FareComponent
    pricing_timestamp: datetime
    score: Optional[float] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class Passenger(BaseModel):
    first_name: str
    last_name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None


# ---------- Intent & Weather ----------

class IntentParseResult(BaseModel):
    success: bool
    criteria: Optional[SearchCriteria] = None
    reasoning: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    raw: Optional[str] = None


class WeatherPoint(BaseModel):
    code: str  # IATA
    name: Optional[str] = None
    latitude: float
    longitude: float
    temperature_c: Optional[float] = None
    wind_speed_kph: Optional[float] = None
    wind_direction_deg: Optional[int] = None
    weather_code: Optional[int] = None
    time: Optional[datetime] = None


class WeatherReport(BaseModel):
    origin: Optional[WeatherPoint] = None
    destination: Optional[WeatherPoint] = None
    fetched_at: datetime
    provider: str = "open-meteo"


# ---------- Booking / Payment / Ticketing ----------

class BookingRequest(BaseModel):
    itinerary_id: str
    passengers: List[Passenger]
    client_reference: str


class BookingRecord(BaseModel):
    booking_id: str
    itinerary: Itinerary
    passengers: List[Passenger]
    created_at: datetime
    status: str
    hold_expires_at: Optional[datetime] = None


class PaymentRequest(BaseModel):
    booking_id: str
    amount: float
    currency: str = "USD"
    card_token: str
    capture: bool = True
    idempotency_key: str


class PaymentResult(BaseModel):
    payment_id: str
    booking_id: str
    authorized_amount: float
    currency: str
    status: str
    processor_ref: Optional[str] = None
    created_at: datetime


class TicketRecord(BaseModel):
    ticket_numbers: List[str]
    booking_id: str
    issued_at: datetime
    status: str
    delivery_channel: str = "EMAIL"


# ---------- Orchestration Planning & Steps ----------

class PlanStep(BaseModel):
    step_id: int
    name: str
    agent: str
    action: str
    args: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class OrchestratorPlan(BaseModel):
    intent: str
    steps: List[PlanStep]


class StepResult(BaseModel):
    step_id: int
    name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    started_at: datetime
    ended_at: datetime


# ---------- Final Answer ----------

def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    if isinstance(value, list):
        if all(isinstance(x, (int, float, str)) for x in value):
            return ", ".join(map(str, value))
        return "\n".join(f"- {x}" for x in value)
    return str(value)

class FinalAnswer(BaseModel):
    answer: str
    key_points: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)

    @field_validator("answer", mode="before")
    @classmethod
    def coerce_answer(cls, v):
        if isinstance(v, str):
            return v
        return _stringify(v)

    @field_validator("key_points", "follow_up_questions", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        if isinstance(v, str):
            return [v]
        if isinstance(v, dict):
            return [f"{k}: {val}" for k, val in v.items()]
        return [str(v)]


class LLMMessage(BaseModel):
    role: str
    content: str