from __future__ import annotations
import json
import os
import re
from datetime import date, timedelta
from typing import Optional

import httpx

from agent_models import SearchCriteria, IntentParseResult

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

SYSTEM_PROMPT = (
    "You convert natural language travel requests into a JSON object with keys: "
    "origin (IATA), destination (IATA), depart_date (YYYY-MM-DD), return_date (YYYY-MM-DD or null), "
    'cabin (ECONOMY|PREMIUM|BUSINESS), adults (int), max_results (int <=20), price_cap (float or null). '
    "If info missing, infer reasonable defaults (next Friday for vague 'next week', adults=1). "
    "Output ONLY valid JSON."
)

IATA_PATTERN = re.compile(r"\b([A-Z]{3})\b")


def _heuristic_parse(text: str) -> IntentParseResult:
    """
    Simple fallback when no API key or model invocation fails.
    """
    upper = text.upper()
    tokens = IATA_PATTERN.findall(upper)
    origin = tokens[0] if tokens else "SFO"
    destination = tokens[1] if len(tokens) > 1 else "JFK"

    today = date.today()
    if "NEXT WEEK" in upper:
        # next Monday
        depart = today + timedelta(days=(7 - today.weekday()))
    elif "TOMORROW" in upper:
        depart = today + timedelta(days=1)
    else:
        depart = today + timedelta(days=7)

    round_trip = any(kw in upper for kw in ["ROUND", "RETURN", "BACK"])
    return_date = depart + timedelta(days=3) if round_trip else None

    if "BUSINESS" in upper:
        cabin = "BUSINESS"
    elif "PREMIUM" in upper:
        cabin = "PREMIUM"
    else:
        cabin = "ECONOMY"

    adults = 1
    m = re.search(r"(\d+)\s*(ADULT|ADULTS|PAX|PEOPLE|PASSENGERS)", upper)
    if m:
        adults = max(1, int(m.group(1)))

    price_cap = None
    pm = re.search(r"UNDER\s*\$?(\d+)", upper)
    if pm:
        price_cap = float(pm.group(1))

    criteria = SearchCriteria(
        origin=origin,
        destination=destination,
        depart_date=depart,
        return_date=return_date,
        cabin=cabin,
        adults=adults,
        max_results=10,
        price_cap=price_cap
    )
    return IntentParseResult(
        success=True,
        criteria=criteria,
        reasoning="Heuristic parse (no LLM).",
        warnings=[],
        raw=text
    )


class IntentAgent:
    """
    Parses natural language travel intent into structured SearchCriteria.
    Accepts an optional api_key injected from secrets_loader to avoid re-reading env every call.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")  # last resort
        self.model = model

    def parse(self, user_text: str) -> IntentParseResult:
        if not self.api_key:
            return _heuristic_parse(user_text)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    OPENAI_CHAT_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "temperature": 0.2,
                        "messages": messages,
                        "response_format": {"type": "json_object"}
                    }
                )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(content)

            criteria = SearchCriteria(
                origin=data["origin"],
                destination=data["destination"],
                depart_date=date.fromisoformat(data["depart_date"]),
                return_date=date.fromisoformat(data["return_date"]) if data.get("return_date") else None,
                cabin=data.get("cabin", "ECONOMY"),
                adults=int(data.get("adults", 1)),
                max_results=min(int(data.get("max_results", 10)), 20),
                price_cap=float(data["price_cap"]) if data.get("price_cap") is not None else None
            )
            return IntentParseResult(
                success=True,
                criteria=criteria,
                reasoning="LLM structured parse",
                raw=content
            )
        except Exception as e:
            fallback = _heuristic_parse(user_text)
            fallback.warnings.append(f"LLM parse failed: {e}")
            return fallback