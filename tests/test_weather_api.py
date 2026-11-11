import httpx

from tests.conftest import settings


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_weather_report(client, mock_api):
    response = client.get("/api/weather", params={"city": "Kraków", "days": 2})

    assert response.status_code == 200
    data = response.json()
    assert data["location"]["name"] == "Kraków"
    assert data["current"]["temperature"] == 6.4
    assert data["current"]["description"] == "Overcast"
    assert [d["description"] for d in data["daily"]] == ["Overcast", "Slight rain"]


def test_unknown_city_returns_404(client, mock_api):
    response = client.get("/api/weather", params={"city": "Atlantis"})
    assert response.status_code == 404
    assert "Atlantis" in response.json()["detail"]


def test_api_failure_returns_502(client, respx_mock):
    respx_mock.get(settings.geocoding_url).mock(return_value=httpx.Response(500))
    response = client.get("/api/weather", params={"city": "Kraków"})
    assert response.status_code == 502


def test_invalid_days_returns_422(client):
    assert client.get("/api/weather", params={"city": "Kraków", "days": 30}).status_code == 422


def test_responses_are_cached(client, mock_api):
    client.get("/api/weather", params={"city": "Kraków"})
    client.get("/api/weather", params={"city": " kraków "})
    assert mock_api.calls.call_count == 2  # one geocoding call + one forecast call

    client.delete("/api/weather/cache")
    client.get("/api/weather", params={"city": "Kraków"})
    assert mock_api.calls.call_count == 4
