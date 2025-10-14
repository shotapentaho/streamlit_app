from urllib.parse import quote
from typing import Optional

def _qe(s: Optional[str]) -> str:
    # Strict percent-encoding for values (spaces -> %20, not "+")
    return quote(str(s), safe="") if s is not None else ""

def _normalize_uber_product(product_type: Optional[str]) -> Optional[str]:
    if not product_type:
        return None
    p = product_type.strip().lower().replace(" ", "")
    mapping = {
        "uberx": "uberX",
        "uberxl": "uberXL",
        "ubercomfort": "uberComfort",
        "ubergreen": "uberGreen",
        "uberblack": "uberBlack",
    }
    return mapping.get(p, product_type)

def _fmt_coord(v: Optional[float]) -> Optional[str]:
    return f"{float(v):.6f}" if v is not None else None

def build_uber_link(
    pickup: Optional[str],
    dropoff: Optional[str],
    product_type: Optional[str] = None,
    client_id: Optional[str] = None,
    pickup_lat: Optional[float] = None,
    pickup_lng: Optional[float] = None,
    dropoff_lat: Optional[float] = None,
    dropoff_lng: Optional[float] = None,
    pickup_nickname: Optional[str] = None,
    dropoff_nickname: Optional[str] = None,
) -> str:
    """
    Build a robust Uber deep link that pre-populates source and destination when possible.

    Reliability tips implemented here:
    - Include both bracketed fields (pickup[latitude], …) and simple forms (pickup=lat,lng).
    - Use percent-encoding (quote), not x-www-form-urlencoded (+).
    - Round coordinates to ~6 decimals.
    """
    base = "https://m.uber.com/ul/"
    parts = ["action=setPickup"]

    # Coerce/round coords once
    plat = _fmt_coord(pickup_lat)
    plng = _fmt_coord(pickup_lng)
    dlat = _fmt_coord(dropoff_lat)
    dlng = _fmt_coord(dropoff_lng)

    # Pickup: prefer explicit coords if present; otherwise my_location or formatted address
    if plat and plng:
        # Simple form
        parts.append(f"pickup={plat}%2C{plng}")  # encode comma in the joined string
        # Bracketed form (include both for robustness)
        parts.append(f"pickup[latitude]={plat}")
        parts.append(f"pickup[longitude]={plng}")
        if pickup:
            parts.append(f"pickup[formatted_address]={_qe(pickup)}")
    else:
        if pickup:
            parts.append(f"pickup[formatted_address]={_qe(pickup)}")
        else:
            parts.append("pickup=my_location")
    if pickup_nickname:
        parts.append(f"pickup[nickname]={_qe(pickup_nickname)}")

    # Dropoff
    if dlat and dlng:
        parts.append(f"dropoff={dlat}%2C{dlng}")
        parts.append(f"dropoff[latitude]={dlat}")
        parts.append(f"dropoff[longitude]={dlng}")
        if dropoff:
            parts.append(f"dropoff[formatted_address]={_qe(dropoff)}")
    else:
        if dropoff:
            parts.append(f"dropoff[formatted_address]={_qe(dropoff)}")
    if dropoff_nickname:
        parts.append(f"dropoff[nickname]={_qe(dropoff_nickname)}")

    # Product type and client id
    pt = _normalize_uber_product(product_type)
    if pt:
        parts.append(f"productType={_qe(pt)}")
    if client_id:
        parts.append(f"client_id={_qe(client_id)}")

    return f"{base}?{'&'.join(parts)}"

def build_instacart_link(
    query: Optional[str],
    address: Optional[str] = None,
    preferred_store: Optional[str] = None,
) -> str:
    """
    Build an Instacart search link with a single q param. Address/store are hints for the query.
    """
    base = "https://www.instacart.com/store/search"
    q_parts: list[str] = []
    if query:
        q_parts.append(query)
    if preferred_store:
        q_parts.append(f"store:{preferred_store}")
    if address:
        q_parts.append(f"near:{address}")
    q = " ".join(q_parts) if q_parts else "groceries"
    return f"{base}?v=2&q={_qe(q)}"

def build_doordash_link(
    query: Optional[str],
    address: Optional[str] = None,
    note: Optional[str] = None,
) -> str:
    """
    Build a DoorDash search link. We encode the query into the path segment.
    """
    if not query and not address and not note:
        query = "food"
    parts = [p for p in [query, note] if p]
    q = " ".join(parts) if parts else "food"
    return f"https://www.doordash.com/search/store/{_qe(q)}"

def build_ubereats_link(
    query: Optional[str],
    address: Optional[str] = None,
    note: Optional[str] = None,
    dining_mode: str = "DELIVERY",
) -> str:
    """
    Build an Uber Eats search link.
    Notes:
    - Uber Eats heavily uses on-site location selection; we provide a best-effort query.
    - We include diningMode=DELIVERY to bias results.
    - Address is appended as a hint inside the query string (site will still prompt for precise location).
    """
    base = "https://www.ubereats.com/search"
    if not query and not note and not address:
        query = "food"
    parts = [p for p in [query, note] if p]
    if address:
        parts.append(f"near:{address}")
    q = " ".join(parts) if parts else "food"
    return f"{base}?query={_qe(q)}&diningMode={_qe(dining_mode)}"