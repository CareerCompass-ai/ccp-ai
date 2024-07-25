from typing import List, Optional

from pydantic import BaseModel

from .tag import Tag


class City(BaseModel):
    city_id: int
    city_name: str
class Country(BaseModel):
    country_id: int
    country_name: str
    city: List[City]

class ListCountry(BaseModel):
    country_id: int
    country_name: str
class ListCommonTypes(BaseModel):
    tag: list[Tag]
    hiring_level: list[str]
    job_type: list[str]
    company_type: list[str]
    work_place: list[str]
    countries: List[ListCountry]
    cities: List[Country]

class CommonTypev2(BaseModel):
    name: str
    count: Optional[int] = 0
class ListCommonTypesv2(BaseModel):
    hiring_levels: list[CommonTypev2]
    job_types: list[CommonTypev2]
    work_places: list[CommonTypev2]
    company_types: list[CommonTypev2]
    cities: List[CommonTypev2]
    countries: List[CommonTypev2]
    job_tags: list[CommonTypev2]
    labels: list[CommonTypev2]
