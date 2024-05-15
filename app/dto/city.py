from typing import List
from pydantic import BaseModel
from datetime import datetime

class CityBase(BaseModel):
    id: int
    country_id: int
    city_name: str
    created_at: datetime
    updated_at: datetime

class ListCityResponse(BaseModel):
    cities: List[CityBase]
