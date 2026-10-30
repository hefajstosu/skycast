from typing import Any

import httpx

from app.config import Settings
from app.schemas import Location


class WeatherApiError(Exception):
    """Error while communicating with the Open-Meteo API."""


class CityNotFoundError(Exception):
    """No city matches the given name."""


class OpenMeteoClient:
    def __init__(self, settings: Settings, http: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._http = http or httpx.AsyncClient(timeout=settings.http_timeout)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self._http.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise WeatherApiError(f"Failed to connect to Open-Meteo: {exc}") from exc
        return response.json()

    async def geocode(self, city: str) -> Location:
        data = await self._get(
            self._settings.geocoding_url,
            {"name": city, "count": 1, "language": self._settings.language, "format": "json"},
        )
        results = data.get("results")
        if not results:
            raise CityNotFoundError(f"City not found: {city}")
        return Location.model_validate(results[0])
