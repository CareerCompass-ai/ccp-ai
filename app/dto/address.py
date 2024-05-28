from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AddressBase(BaseModel):
    id: Optional[int] = None
    city_id: Optional[int] = None
    detailed_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ListAddressResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[AddressBase]
