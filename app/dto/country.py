from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CountryBase(BaseModel):
    id: Optional[int] = None
    country_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListCountryResponse(BaseModel):
    countries: List[CountryBase]
