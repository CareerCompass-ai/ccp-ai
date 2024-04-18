from typing import List, Optional
from pydantic import BaseModel

from .tag import Tag

import constant.common as constant

class ListCommonTypes(BaseModel):
    tag: list[Tag]
    hiring_level: list[str]
    job_type: list[str]
    company_type: list[str]
    work_place: list[str]
