from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
class CityBase(BaseModel):
    id: Optional[int] = None
    country_id: Optional[int] = None
    city_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
class ListCityResponse(BaseModel):
    cities: List[CityBase]
