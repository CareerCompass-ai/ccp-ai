from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class UserBase(BaseModel):
    id: Optional[int] = None
    image_id: Optional[int] = None
    address_id: Optional[int] = None
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserAggregate(UserBase):
    matching_score: Optional[float] = None

