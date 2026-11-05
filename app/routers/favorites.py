import asyncio

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from app.clients.open_meteo import CityNotFoundError, WeatherApiError
from app.database import DbSession
from app.dependencies import WeatherClient
from app.models import Favorite
from app.schemas import FavoriteCreate, FavoriteRead, FavoriteWeather

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteRead])
def list_favorites(db: DbSession) -> list[Favorite]:
    return list(db.scalars(select(Favorite).order_by(Favorite.city)))


@router.post("", response_model=FavoriteRead, status_code=201)
async def add_favorite(payload: FavoriteCreate, db: DbSession, client: WeatherClient) -> Favorite:
    # make sure the city exists and store its official name
    try:
        location = await client.geocode(payload.city)
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WeatherApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if db.scalar(select(Favorite).where(Favorite.city == location.name)):
        raise HTTPException(status_code=409, detail=f"{location.name} is already in favorites")

    favorite = Favorite(city=location.name, note=payload.note)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{favorite_id}", status_code=204)
def delete_favorite(favorite_id: int, db: DbSession) -> Response:
    favorite = db.get(Favorite, favorite_id)
    if favorite is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return Response(status_code=204)


@router.get("/weather", response_model=list[FavoriteWeather])
async def favorites_weather(db: DbSession, client: WeatherClient) -> list[FavoriteWeather]:
    favorites = list(db.scalars(select(Favorite).order_by(Favorite.city)))

    async def fetch(favorite: Favorite) -> FavoriteWeather:
        read = FavoriteRead.model_validate(favorite)
        try:
            report = await client.get_report(favorite.city, days=1)
        except (CityNotFoundError, WeatherApiError) as exc:
            return FavoriteWeather(favorite=read, current=None, error=str(exc))
        return FavoriteWeather(favorite=read, current=report.current)

    return list(await asyncio.gather(*(fetch(f) for f in favorites)))
