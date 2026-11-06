from typing import Any

import httpx

from app.cache import TTLCache
from app.config import Settings
from app.schemas import CurrentWeather, DailyForecast, Location, WeatherReport
from app.weather_codes import describe


class WeatherApiError(Exception):
    """Error while communicating with the Open-Meteo API."""


class CityNotFoundError(Exception):
    """No city matches the given name."""


class OpenMeteoClient:
    def __init__(self, settings: Settings, http: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._http = http or httpx.AsyncClient(timeout=settings.http_timeout)
        self._locations: TTLCache[Location] = TTLCache(settings.cache_ttl_seconds)
        self._reports: TTLCache[WeatherReport] = TTLCache(settings.cache_ttl_seconds)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _get(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self._http.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise WeatherApiError(f"Failed to connect to Open-Meteo: {exc}") from exc
        return response.json()

    def clear_cache(self) -> None:
        self._locations.clear()
        self._reports.clear()

    async def geocode(self, city: str) -> Location:
        key = city.strip().lower()
        if cached := self._locations.get(key):
            return cached
        data = await self._get(
            self._settings.geocoding_url,
            {"name": city, "count": 1, "language": self._settings.language, "format": "json"},
        )
        results = data.get("results")
        if not results:
            raise CityNotFoundError(f"City not found: {city}")
        location = Location.model_validate(results[0])
        self._locations.set(key, location)
        return location

    async def forecast(self, location: Location, days: int = 7) -> WeatherReport:
        data = await self._get(
            self._settings.forecast_url,
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                "wind_speed_10m,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": location.timezone,
                "forecast_days": days,
            },
        )
        try:
            return self._parse_forecast(location, data)
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherApiError(f"Unexpected response format: {exc}") from exc

    async def get_report(self, city: str, days: int = 7) -> WeatherReport:
        key = (city.strip().lower(), days)
        if cached := self._reports.get(key):
            return cached
        location = await self.geocode(city)
        report = await self.forecast(location, days)
        self._reports.set(key, report)
        return report

    @staticmethod
    def _parse_forecast(location: Location, data: dict[str, Any]) -> WeatherReport:
        cur = data["current"]
        current = CurrentWeather(
            time=cur["time"],
            temperature=cur["temperature_2m"],
            apparent_temperature=cur["apparent_temperature"],
            humidity=cur["relative_humidity_2m"],
            wind_speed=cur["wind_speed_10m"],
            weather_code=cur["weather_code"],
            description=describe(cur["weather_code"]),
        )
        d = data["daily"]
        daily = [
            DailyForecast(
                day=day,
                temp_max=t_max,
                temp_min=t_min,
                precipitation=rain,
                weather_code=code,
                description=describe(code),
            )
            for day, t_max, t_min, rain, code in zip(
                d["time"],
                d["temperature_2m_max"],
                d["temperature_2m_min"],
                d["precipitation_sum"],
                d["weather_code"],
                strict=True,
            )
        ]
        return WeatherReport(location=location, current=current, daily=daily)
