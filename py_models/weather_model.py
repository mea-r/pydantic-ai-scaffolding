from pydantic import BaseModel
from typing import Optional

class WeatherModel(BaseModel):
    location: Optional[str] = None
    temperature: Optional[float] = None
    conditions: Optional[str] = None
