from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AddressBase(BaseModel):
    id: Optional[int] = None
    city_id: int
    detailed_address: str
    created_at: datetime
    updated_at: datetime

class ListAddressResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[AddressBase]
