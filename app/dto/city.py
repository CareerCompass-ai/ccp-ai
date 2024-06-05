from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CityBase(BaseModel):
    id: int
    country_id: int
    city_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
class ListCityResponse(BaseModel):
    cities: List[CityBase]
