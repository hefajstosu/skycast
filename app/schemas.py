from pydantic import BaseModel


class Location(BaseModel):
    name: str
    country: str | None = None
    latitude: float
    longitude: float
    timezone: str = "auto"
