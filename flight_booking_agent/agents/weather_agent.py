from __future__ import annotations
from typing import Optional, Dict
from datetime import datetime
import httpx

from agent_models import WeatherReport, WeatherPoint

# Minimal airport -> (name, lat, lon)
AIRPORT_COORDS: Dict[str, tuple] = {
    "SFO": ("San Francisco Intl", 37.6213, -122.3790),
    "JFK": ("John F Kennedy Intl", 40.6413, -73.7781),
    "LAX": ("Los Angeles Intl", 33.9416, -118.4085),
    "ORD": ("Chicago O'Hare", 41.9742, -87.9073),
    "SEA": ("Seattle Tacoma Intl", 47.4502, -122.3088),
    "DFW": ("Dallas/Fort Worth", 32.8998, -97.0403),
}

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def _fetch_point(code: str) -> Optional[WeatherPoint]:
    meta = AIRPORT_COORDS.get(code.upper())
    if not meta:
        return None
    name, lat, lon = meta
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "windspeed_unit": "kmh"
        }
        with httpx.Client(timeout=10.0) as client:
            r = client.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        data = r.json()
        cw = data.get("current_weather", {})
        return WeatherPoint(
            code=code.upper(),
            name=name,
            latitude=lat,
            longitude=lon,
            temperature_c=cw.get("temperature"),
            wind_speed_kph=cw.get("windspeed"),
            wind_direction_deg=cw.get("winddirection"),
            weather_code=cw.get("weathercode"),
            time=datetime.fromisoformat(cw["time"]) if cw.get("time") else None
        )
    except Exception:
        return WeatherPoint(
            code=code.upper(),
            name=name,
            latitude=lat,
            longitude=lon
        )

class WeatherAgent:
    def get_report(self, origin_code: str, destination_code: str) -> WeatherReport:
        origin = _fetch_point(origin_code)
        destination = _fetch_point(destination_code)
        return WeatherReport(
            origin=origin,
            destination=destination,
            fetched_at=datetime.utcnow()
        )