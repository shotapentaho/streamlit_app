import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # OpenAI SDK optional


Service = str  # "uber" | "instacart" | "doordash" | "ubereats"

@dataclass
class Intent:
    service: Optional[Service] = None
    # Uber (rides)
    pickup: Optional[str] = None
    dropoff: Optional[str] = None
    ride_type: Optional[str] = None
    # Instacart
    items: Optional[str] = None
    preferred_store: Optional[str] = None
    address: Optional[str] = None
    # DoorDash / UberEats
    query: Optional[str] = None
    note: Optional[str] = None


def merge_partial_intent(base: Intent, patch: Dict[str, Any]) -> Intent:
    data = base.__dict__.copy()
    for k, v in patch.items():
        if v is not None and v != "":
            data[k] = v
    return Intent(**data)


class ServiceAgent:
    def __init__(self, api_key: Optional[str], model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key) if (api_key and OpenAI) else None

    # ------------------------
    # Public API
    # ------------------------
    def build_links(self, user_text: str) -> Dict[str, Any]:
        readable = self._normalize_request(user_text)
        intent = self.parse_intent(user_text)
        s = self._normalize_service(intent.service)

        if s == "uber":
            entry = self._build_uber_entry(intent)
            return {"readable_request": readable, "services": [entry]}
        if s == "instacart":
            entry = self._build_instacart_entry(intent)
            return {"readable_request": readable, "services": [entry]}
        if s == "doordash":
            entry = self._build_doordash_entry(intent)
            return {"readable_request": readable, "services": [entry]}
        if s == "ubereats":
            entry = self._build_ubereats_entry(intent)
            return {"readable_request": readable, "services": [entry]}

        return self.build_links_for_all_services(user_text)

    def build_links_for_all_services(self, user_text: str) -> Dict[str, Any]:
        readable = self._normalize_request(user_text)
        intent = self.parse_intent(user_text)

        uber_entry = self._build_uber_entry(Intent(service="uber", pickup=intent.pickup, dropoff=intent.dropoff, ride_type=intent.ride_type))
        instacart_entry = self._build_instacart_entry(Intent(service="instacart", items=intent.items, preferred_store=intent.preferred_store, address=intent.address))
        doordash_entry = self._build_doordash_entry(Intent(service="doordash", query=intent.query, address=intent.address, note=intent.note))
        ubereats_entry = self._build_ubereats_entry(Intent(service="ubereats", query=intent.query, address=intent.address, note=intent.note))

        return {"readable_request": readable, "services": [uber_entry, instacart_entry, doordash_entry, ubereats_entry]}

    # ------------------------
    # Entry Builders
    # ------------------------
    def _build_uber_entry(self, uber_intent: Intent) -> Dict[str, Any]:
        from utils.deeplinks import build_uber_link
        self._apply_defaults(uber_intent)

        geo_notes: List[str] = []
        pickup_lat = pickup_lng = dropoff_lat = dropoff_lng = None

        p_geo = self._geocode_safe(uber_intent.pickup)
        if p_geo:
            pickup_lat, pickup_lng = p_geo["lat"], p_geo["lng"]
            uber_intent.pickup = p_geo.get("label", uber_intent.pickup)
            geo_notes.append(f"pickup resolved to '{uber_intent.pickup}'")

        d_geo = self._geocode_safe(uber_intent.dropoff)
        if d_geo:
            dropoff_lat, dropoff_lng = d_geo["lat"], d_geo["lng"]
            uber_intent.dropoff = d_geo.get("label", uber_intent.dropoff)
            geo_notes.append(f"dropoff resolved to '{uber_intent.dropoff}'")

        pickup_nick = self._guess_nickname(uber_intent.pickup)
        dropoff_nick = self._guess_nickname(uber_intent.dropoff)

        url = build_uber_link(
            pickup=uber_intent.pickup,
            dropoff=uber_intent.dropoff,
            product_type=uber_intent.ride_type,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            dropoff_lat=dropoff_lat,
            dropoff_lng=dropoff_lng,
            pickup_nickname=pickup_nick,
            dropoff_nickname=dropoff_nick,
        )
        return {"service": "Uber", "url": url, "summary": self._summary(uber_intent), "assumptions": self._assumptions(uber_intent) + (geo_notes or [])}

    def _build_instacart_entry(self, instacart_intent: Intent) -> Dict[str, Any]:
        from utils.deeplinks import build_instacart_link
        self._apply_defaults(instacart_intent)
        url = build_instacart_link(instacart_intent.items, address=instacart_intent.address, preferred_store=instacart_intent.preferred_store)
        return {"service": "Instacart", "url": url, "summary": self._summary(instacart_intent), "assumptions": self._assumptions(instacart_intent)}

    def _build_doordash_entry(self, doordash_intent: Intent) -> Dict[str, Any]:
        from utils.deeplinks import build_doordash_link
        self._apply_defaults(doordash_intent)
        url = build_doordash_link(query=doordash_intent.query, address=doordash_intent.address, note=doordash_intent.note)
        return {"service": "DoorDash", "url": url, "summary": self._summary(doordash_intent), "assumptions": self._assumptions(doordash_intent)}

    def _build_ubereats_entry(self, eats_intent: Intent) -> Dict[str, Any]:
        from utils.deeplinks import build_ubereats_link
        # Ensure we always carry the user's food choice in the link
        self._apply_defaults(eats_intent)
        if not eats_intent.query:
            eats_intent.query = self._extract_food_query(self._last_user_text) or "food"
        url = build_ubereats_link(query=eats_intent.query, address=eats_intent.address, note=eats_intent.note)
        return {"service": "Uber Eats", "url": url, "summary": self._summary(eats_intent, service_override="ubereats"), "assumptions": self._assumptions(eats_intent, service_override="ubereats")}

    # ------------------------
    # Core intent parsing
    # ------------------------
    def parse_intent(self, user_text: str) -> Intent:
        # keep the last user text for fallback extraction in _build_ubereats_entry
        self._last_user_text = user_text

        if self.client:
            try:
                system = (
                    "You convert user requests into a single JSON object describing a service intent. "
                    "Services: uber, instacart, doordash, ubereats. "
                    "Fields by service:\n"
                    "- uber: pickup (string|optional), dropoff (string|optional), ride_type (string|optional)\n"
                    "- instacart: items (string|optional), preferred_store (string|optional), address (string|optional)\n"
                    "- doordash: query (string|optional), address (string|optional), note (string|optional)\n"
                    "- ubereats: query (string|optional), address (string|optional), note (string|optional)\n"
                    "Rules:\n"
                    "- Choose the single most appropriate service.\n"
                    "- If the user mentions a specific service, use it.\n"
                    "- If address is like 'home', 'office', keep as is (do not invent addresses).\n"
                    "- Respond with ONLY JSON, no markdown.\n"
                )
                user = f"User: {user_text}\nReturn JSON with keys: service, pickup, dropoff, ride_type, items, preferred_store, address, query, note."
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    temperature=0.2,
                )
                raw = resp.choices[0].message.content or ""
                data = self._extract_json(raw)
                service = self._normalize_service(data.get("service"))
                intent = Intent(
                    service=service or self._guess_service(user_text),
                    pickup=data.get("pickup"),
                    dropoff=data.get("dropoff"),
                    ride_type=data.get("ride_type"),
                    items=data.get("items"),
                    preferred_store=data.get("preferred_store"),
                    address=data.get("address"),
                    query=data.get("query"),
                    note=data.get("note"),
                )
                # Ensure food services carry a query
                s = self._normalize_service(intent.service)
                if s in {"doordash", "ubereats"} and not intent.query:
                    intent.query = self._extract_food_query(user_text)
                return intent
            except Exception:
                pass

        return self._heuristic_parse(user_text)

    # ------------------------
    # Helpers
    # ------------------------
    def _extract_food_query(self, text: str) -> Optional[str]:
        """
        Extract a dish/restaurant/cuisine from free text.
        Priority: quoted text > after service/verbs > known cuisines.
        """
        if not text:
            return None
        t = text.strip()

        # 1) Quoted phrase: "pepperoni pizza", 'McDonald’s'
        m = re.findall(r"['\"]([^'\"]+)['\"]", t)
        if m:
            return m[-1].strip()

        lo = t.lower()

        # 2) After explicit service mentions (ubereats/uber eats or doordash/door dash)
        m2 = re.search(r"(?:uber\s*eats|ubereats|door\s*dash|doordash)\s+(?:for|about|on|search(?:ing)?\s+for|order(?:ing)?(?:\s+from)?|get|find)?\s*(.+)", lo)
        if m2:
            candidate = m2.group(1)
            # cut off trailing location hints
            candidate = re.split(r"\b(?:near|in|at)\b", candidate)[0]
            return candidate.strip(" .,!?:;")

        # 3) After generic "order"/"find" verbs
        m3 = re.search(r"(?:order|find|get)\s+(.*)", lo)
        if m3:
            candidate = m3.group(1)
            candidate = re.split(r"\b(?:near|in|at)\b", candidate)[0]
            return candidate.strip(" .,!?:;")

        # 4) Known cuisines keywords
        cuisines = ["sushi", "pizza", "burger", "ramen", "tacos", "thai", "indian", "mexican", "chinese", "italian", "kebab", "shawarma", "dimsum", "noodles", "bbq"]
        for c in cuisines:
            if c in lo:
                return c

        return None

    def _geocode_safe(self, text: Optional[str]) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        try:
            from utils.geocode import geocode_one
            return geocode_one(text)
        except Exception:
            return None

    def _apply_defaults(self, intent: Intent) -> None:
        s = self._normalize_service(intent.service)
        if s == "uber":
            if intent.ride_type:
                intent.ride_type = intent.ride_type.strip()
        elif s == "instacart":
            if not intent.items:
                intent.items = "groceries"
        elif s in {"doordash", "ubereats"}:
            if not intent.query:
                intent.query = "food"

    def _summary(self, intent: Intent, service_override: Optional[str] = None) -> str:
        s = self._normalize_service(service_override or intent.service)
        if s == "uber":
            parts = ["Uber"]
            parts.append(f"from '{intent.pickup}'" if intent.pickup else "(pickup: current location)")
            if intent.dropoff:
                parts.append(f"to '{intent.dropoff}'")
            if intent.ride_type:
                parts.append(f"[{intent.ride_type}]")
            return " ".join(parts)
        if s == "instacart":
            parts = ["Instacart search"]
            if intent.items:
                parts.append(f"for '{intent.items}'")
            if intent.preferred_store:
                parts.append(f"at '{intent.preferred_store}'")
            if intent.address:
                parts.append(f"near '{intent.address}'")
            return " ".join(parts)
        if s == "doordash":
            parts = ["DoorDash search"]
            if intent.query:
                parts.append(f"for '{intent.query}'")
            if intent.note:
                parts.append(f"({intent.note})")
            return " ".join(parts)
        if s == "ubereats":
            parts = ["Uber Eats search"]
            if intent.query:
                parts.append(f"for '{intent.query}'")
            if intent.note:
                parts.append(f"({intent.note})")
            return " ".join(parts)
        return "Open link"

    def _assumptions(self, intent: Intent, service_override: Optional[str] = None) -> List[str]:
        s = self._normalize_service(service_override or intent.service)
        assumptions: List[str] = []
        if s == "uber":
            if not intent.pickup:
                assumptions.append("pickup will use current location")
            if not intent.dropoff:
                assumptions.append("destination will be chosen in the app")
        elif s == "instacart":
            if intent.items == "groceries":
                assumptions.append("no specific items provided; used 'groceries'")
        elif s in {"doordash", "ubereats"}:
            if intent.query == "food":
                assumptions.append("no specific cuisine/dish provided; used 'food'")
        return assumptions

    def _normalize_request(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return "(empty request)"
        t = t[0].upper() + t[1:]
        if t[-1] not in ".!?":
            t += "."
        return t

    def _normalize_service(self, s: Optional[str]) -> Optional[str]:
        if not s:
            return None
        ss = s.strip().lower().replace("_", "").replace(" ", "")
        if ss in {"ubereats", "eats"}:
            return "ubereats"
        if ss in {"doordash"}:
            return "doordash"
        if ss in {"uber"}:
            return "uber"
        if ss in {"instacart"}:
            return "instacart"
        return s.strip().lower()

    def _guess_service(self, text: str) -> Optional[Service]:
        lowered = text.lower()
        if "uber eats" in lowered or "ubereats" in lowered or ("eats" in lowered and "uber" in lowered):
            return "ubereats"
        if "uber" in lowered or "ride" in lowered or re.search(r"\bto\s+.+", lowered):
            return "uber"
        if "instacart" in lowered or "grocer" in lowered or "costco" in lowered or "safeway" in lowered:
            return "instacart"
        if "doordash" in lowered or "restaurant" in lowered or "order food" in lowered or "deliver" in lowered:
            return "doordash"
        if any(k in lowered for k in ["sushi", "pizza", "tacos", "ramen", "burger", "thai", "indian", "mexican", "chinese", "italian"]):
            return "doordash"
        if any(k in lowered for k in ["milk", "eggs", "bread", "grocery", "vegetable", "fruit"]):
            return "instacart"
        return None

    def _heuristic_parse(self, text: str) -> Intent:
        lowered = text.lower()
        service = self._normalize_service(self._guess_service(text))
        intent = Intent(service=service)

        if service == "uber":
            m = re.search(r"\bfrom\s+(.+?)\s+to\s+(.+)", text, flags=re.IGNORECASE)
            if m:
                intent.pickup = m.group(1).strip()
                intent.dropoff = m.group(2).strip()
            else:
                m2 = re.search(r"\bto\s+(.+)", text, flags=re.IGNORECASE)
                if m2:
                    intent.dropoff = m2.group(1).strip()
            for rt in ["uberx", "uber xl", "uberxl", "uber black", "uber green", "uber comfort"]:
                if rt in lowered:
                    intent.ride_type = rt.replace(" ", "")
                    break

        elif service == "instacart":
            if any(k in lowered for k in ["milk", "eggs", "bread", "banana", "apple", "grocery", "list", "cart"]):
                intent.items = text.strip()
            m = re.search(r"\b(?:at|from)\s+(costco|safeway|whole foods|trader joe'?s|walmart)\b", lowered)
            if m:
                intent.preferred_store = m.group(1)

        elif service in {"doordash", "ubereats"}:
            # Always try to extract user’s food choice into the query
            q = self._extract_food_query(text)
            if q:
                intent.query = q
            else:
                cuisines = ["sushi", "pizza", "burger", "ramen", "tacos", "thai", "indian", "mexican", "chinese", "italian"]
                for c in cuisines:
                    if c in lowered:
                        intent.query = c
                        break

        return intent

    def _guess_nickname(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        t = text.strip()
        low = t.lower()
        if "home" in low:
            return "Home"
        if "office" in low or "work" in low:
            return "Office"
        m = re.search(r"\b([A-Z]{3,4})\b", t)
        if m:
            return m.group(1)
        return t.split(",")[0][:24]

    def _last_quoted(self, text: str) -> Optional[str]:
        m = re.findall(r"['\"]([^'\"]+)['\"]", text)
        if m:
            return m[-1]
        return None

    def _extract_json(self, s: str) -> Dict[str, Any]:
        try:
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(s[start:end+1])
        except Exception:
            pass
        return {}