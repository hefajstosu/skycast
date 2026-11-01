from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.open_meteo import OpenMeteoClient
from app.config import get_settings
from app.routers import weather

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.weather_client = OpenMeteoClient(settings)
    yield
    await app.state.weather_client.aclose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(weather.router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
