from datetime import date, datetime

from pydantic import BaseModel


class Location(BaseModel):
    name: str
    country: str | None = None
    latitude: float
    longitude: float
    timezone: str = "auto"


class CurrentWeather(BaseModel):
    time: datetime
    temperature: float
    apparent_temperature: float
    humidity: int
    wind_speed: float
    weather_code: int
    description: str


class DailyForecast(BaseModel):
    day: date
    temp_max: float
    temp_min: float
    precipitation: float
    weather_code: int
    description: str


class WeatherReport(BaseModel):
    location: Location
    current: CurrentWeather
    daily: list[DailyForecast]
