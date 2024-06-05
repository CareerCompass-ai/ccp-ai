from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CertificateBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    certificate_name: Optional[str] = ""
    organization: Optional[str] = ""
    date: Optional[datetime] = None
    link: Optional[str] = ""
    detail: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None