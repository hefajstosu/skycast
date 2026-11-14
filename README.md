# Skycast

A Python web app that shows current weather and a forecast of up to 16 days for any
city, and lets you save your favorite places. Data comes from the free
[Open-Meteo](https://open-meteo.com/) API, which requires no API key.

## Stack

| Role | Tool |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| External API | Open-Meteo (geocoding + forecast) |
| HTTP client | httpx (async) |
| Validation / configuration | Pydantic, pydantic-settings |
| Database | SQLAlchemy 2.0 + SQLite |
| HTML templates | Jinja2 |
| Tests | pytest + respx (httpx mocking) |

## Running

Requires Python 3.12+.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

- app: http://127.0.0.1:8000
- API docs (Swagger): http://127.0.0.1:8000/docs

### Docker

```bash
docker build -t skycast .
docker run -p 8000:8000 -v skycast-data:/data skycast
```

## Configuration

Environment variables prefixed with `SKYCAST_` (or a `.env` file, see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `SKYCAST_DATABASE_URL` | `sqlite:///./skycast.db` | database URL |
| `SKYCAST_CACHE_TTL_SECONDS` | `600` | API response cache lifetime |
| `SKYCAST_LANGUAGE` | `en` | language of city names |
| `SKYCAST_HTTP_TIMEOUT` | `10` | Open-Meteo request timeout (s) |

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/weather?city=London&days=7` | current weather + forecast |
| DELETE | `/api/weather/cache` | clear the cache |
| GET | `/api/favorites` | list favorite cities |
| POST | `/api/favorites` | add a city `{"city": "...", "note": "..."}` |
| DELETE | `/api/favorites/{id}` | remove a city |
| GET | `/api/favorites/weather` | current weather for all favorites |
| GET | `/health` | health check |

## Tests

```bash
pytest
```

Tests never hit the network: Open-Meteo responses are mocked with respx
and the database runs in memory.

## Structure

```
app/
├── main.py              # FastAPI app, lifespan, routers
├── config.py            # settings (pydantic-settings)
├── clients/open_meteo.py# API client with caching
├── cache.py             # TTL cache
├── database.py, models.py
├── schemas.py           # Pydantic models
├── weather_codes.py     # WMO weather code descriptions
├── routers/             # weather, favorites, pages
├── templates/, static/  # frontend
tests/
```
