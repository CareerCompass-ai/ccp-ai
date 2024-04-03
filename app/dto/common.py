from typing import List, Optional
from pydantic import BaseModel

from .tag import Tag

import constant.common as constant

class ListCommonTypes(BaseModel):
    tags: list[Tag]
    hiring_levels: list[str]
    job_types: list[str]
    company_types: list[str]
    work_places: list[str]
