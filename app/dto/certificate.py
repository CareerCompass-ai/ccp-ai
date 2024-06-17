from datetime import datetime, date as l_date
from typing import Optional

from pydantic import BaseModel


class CertificateBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    certificate_name: Optional[str] = ""
    organization: Optional[str] = ""
    date: Optional[l_date] = ""
    link: Optional[str] = ""
    detail: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None