from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.clients.open_meteo import CityNotFoundError, WeatherApiError
from app.dependencies import WeatherClient
from app.schemas import WeatherReport

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("", response_model=WeatherReport)
async def get_weather(
    client: WeatherClient,
    city: Annotated[str, Query(min_length=1, max_length=100)],
    days: Annotated[int, Query(ge=1, le=16)] = 7,
) -> WeatherReport:
    try:
        return await client.get_report(city, days)
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WeatherApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.delete("/cache", status_code=204)
def clear_cache(client: WeatherClient) -> None:
    client.clear_cache()
