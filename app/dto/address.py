from typing import List
from pydantic import BaseModel
from datetime import datetime

class AddressBase(BaseModel):
    id: int
    city_id: int
    detailed_address: str
    created_at: datetime
    updated_at: datetime

class ListAddressResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[AddressBase]
