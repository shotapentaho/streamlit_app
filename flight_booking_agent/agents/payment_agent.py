from __future__ import annotations
from agent_models import PaymentRequest, PaymentResult
from agent_tools import authorize_payment

class PaymentAgent:
    name = "payment_agent"

    def authorize(self, pr: PaymentRequest) -> PaymentResult:
        return authorize_payment(pr)