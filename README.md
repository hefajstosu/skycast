# Skycast

Weather for any city, right now and up to 16 days ahead, plus a list of
favorite places. Built as a small FastAPI app on top of the free
[Open-Meteo](https://open-meteo.com/) API — no API key needed, which is the
whole reason I picked it.

## Stack

FastAPI + SQLAlchemy (SQLite) + Jinja2, with httpx for the Open-Meteo calls and
pydantic-settings for config. Tests use pytest and respx so they never hit the
network.

## Running

Python 3.12 or newer.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

- app: http://127.0.0.1:8000
- swagger: http://127.0.0.1:8000/docs

### Docker

```bash
docker build -t skycast .
docker run -p 8000:8000 -v skycast-data:/data skycast
```

## Configuration

Everything is set through env vars prefixed with `SKYCAST_` (or a `.env` file,
see `.env.example`):

- `SKYCAST_DATABASE_URL` — database URL (default `sqlite:///./skycast.db`)
- `SKYCAST_CACHE_TTL_SECONDS` — how long API responses stay cached (default `600`)
- `SKYCAST_LANGUAGE` — language of city names from geocoding (default `en`)
- `SKYCAST_HTTP_TIMEOUT` — Open-Meteo request timeout in seconds (default `10`)

## API

- `GET /api/weather?city=London&days=7` — current weather + forecast
- `DELETE /api/weather/cache` — clear the response cache
- `GET /api/favorites` — list favorite cities
- `POST /api/favorites` — add a city (`{"city": "...", "note": "..."}`)
- `DELETE /api/favorites/{id}` — remove a city
- `GET /api/favorites/weather` — current weather for every favorite
- `GET /health` — health check

## Tests

```bash
pytest
```

Open-Meteo is mocked with respx and the database runs in memory, so the suite
doesn't need internet access.

## Known quirks

- The response cache is a plain in-memory dict with a TTL and never evicts
  entries that aren't re-read. Fine at this scale, but it'd grow without bound
  under real traffic — there's a TODO in `app/cache.py`.
- Favorite weather is fetched one city at a time (`asyncio.gather`), not batched
  by coordinates.

## Structure

```
app/
├── main.py              # app setup, lifespan, routers
├── config.py            # settings
├── clients/open_meteo.py# API client + caching
├── cache.py             # TTL cache
├── database.py, models.py
├── schemas.py           # pydantic models
├── weather_codes.py     # WMO code -> description
├── routers/             # weather, favorites, pages
├── templates/, static/  # frontend
tests/
```
