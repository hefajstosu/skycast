from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.clients.open_meteo import CityNotFoundError, WeatherApiError
from app.config import get_settings
from app.database import DbSession
from app.dependencies import WeatherClient
from app.models import Favorite

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: DbSession,
    client: WeatherClient,
    city: Annotated[str | None, Query(max_length=100)] = None,
) -> HTMLResponse:
    report, error, status_code = None, None, 200
    if city and city.strip():
        try:
            report = await client.get_report(city.strip())
        except CityNotFoundError as exc:
            error, status_code = str(exc), 404
        except WeatherApiError:
            status_code = 502
            error = "The weather service is temporarily unavailable. Please try again shortly."

    favorites = list(db.scalars(select(Favorite).order_by(Favorite.city)))
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": get_settings().app_name,
            "city": city or "",
            "report": report,
            "error": error,
            "favorites": favorites,
            "favorite_cities": {f.city for f in favorites},
        },
        status_code=status_code,
    )
