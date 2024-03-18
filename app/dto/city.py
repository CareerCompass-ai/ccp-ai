from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class CityBase(BaseModel):
    id: int
    country_id: int
    city_name: str
    created_at: datetime
    updated_at: datetime

class ListCityResponse(BaseModel):
    cities: List[CityBase]
