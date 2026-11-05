from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


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


class FavoriteCreate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    note: str | None = Field(default=None, max_length=200)


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    city: str
    note: str | None
    created_at: datetime


class FavoriteWeather(BaseModel):
    favorite: FavoriteRead
    current: CurrentWeather | None
    error: str | None = None
