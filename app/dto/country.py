from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class CountryBase(BaseModel):
    id: int
    country_name: str
    created_at: datetime
    updated_at: datetime

class ListCountryResponse(BaseModel):
    countries: List[CountryBase]
