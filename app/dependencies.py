from typing import Annotated

from fastapi import Depends, Request

from app.clients.open_meteo import OpenMeteoClient


def get_weather_client(request: Request) -> OpenMeteoClient:
    return request.app.state.weather_client


WeatherClient = Annotated[OpenMeteoClient, Depends(get_weather_client)]
