import os

# the in-memory database must be configured before importing the app
os.environ["SKYCAST_DATABASE_URL"] = "sqlite://"

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

settings = get_settings()

GEO_KRAKOW = {
    "results": [
        {
            "name": "Kraków",
            "country": "Poland",
            "latitude": 50.06,
            "longitude": 19.94,
            "timezone": "Europe/Warsaw",
        }
    ]
}

FORECAST_KRAKOW = {
    "current": {
        "time": "2026-11-17T12:00",
        "temperature_2m": 6.4,
        "apparent_temperature": 3.1,
        "relative_humidity_2m": 81,
        "wind_speed_10m": 12.5,
        "weather_code": 3,
    },
    "daily": {
        "time": ["2026-11-17", "2026-11-18"],
        "weather_code": [3, 61],
        "temperature_2m_max": [7.0, 8.2],
        "temperature_2m_min": [1.5, 2.0],
        "precipitation_sum": [0.0, 4.3],
    },
}


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_api(respx_mock):
    """Mocks Open-Meteo: Kraków exists, no other city does."""

    def geocoding(request: httpx.Request) -> httpx.Response:
        name = request.url.params["name"].lower()
        if name in ("kraków", "krakow"):
            return httpx.Response(200, json=GEO_KRAKOW)
        return httpx.Response(200, json={})

    respx_mock.get(settings.geocoding_url).mock(side_effect=geocoding)
    respx_mock.get(settings.forecast_url).mock(return_value=httpx.Response(200, json=FORECAST_KRAKOW))
    return respx_mock
