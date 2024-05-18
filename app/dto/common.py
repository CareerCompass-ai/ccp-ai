from pydantic import BaseModel
from typing import List
from .tag import Tag

class ListCommonTypes(BaseModel):
    tag: list[Tag]
    hiring_level: list[str]
    job_type: list[str]
    company_type: list[str]
    work_place: list[str]

class City(BaseModel):
    city_id: int
    city_name: str
class Country(BaseModel):
    country_id: int
    country_name: str
    city: List[City]
class ListCountry(BaseModel):
    records: List[Country]
