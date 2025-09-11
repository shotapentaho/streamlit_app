from __future__ import annotations
from agent_models import BookingRecord, PaymentResult, TicketRecord
from agent_tools import issue_tickets

class TicketingAgent:
    name = "ticketing_agent"

    def issue(self, booking: BookingRecord, payment: PaymentResult) -> TicketRecord:
        return issue_tickets(booking, payment)