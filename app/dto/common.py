from typing import List, Optional
from pydantic import BaseModel

from .tag import Tag

class ListCommonTypes(BaseModel):
    tags: list[Tag]
