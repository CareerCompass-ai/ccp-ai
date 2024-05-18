from fastapi import status, HTTPException, APIRouter
import traceback

from app.dto import common

from app.repo.tag_repo import TagRepository 
from app.repo.country_repo import CountryRepository
from app.repo.city_repo import CityRepository

from models.ccp_country import Country

from config.postgres import PostgresDB
import constant.common as constant

from pkg.logging import logger

common_router = APIRouter(
    prefix="/api",
    tags=['Common']
)

tag_repo = TagRepository()
country_repo = CountryRepository()
city_repo = CityRepository()

@common_router.get("/common/types", response_model=common.ListCommonTypes)
async def list_common_types():
    try:
        tags = await tag_repo.list_tag()

        data = common.ListCommonTypes(
            tag=tags,
            hiring_level=constant.HIRING_LEVELS,
            job_type=constant.JOB_TYPES,
            company_type=constant.COMPANY_TYPES,
            work_place=constant.WORK_PLACES,
        )

        return data
    except Exception:
        logger.error(f"list_common_types failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@common_router.get("/common/city", response_model=common.ListCountry)
async def list_cities_in_countries():
    try:
        rec_countries = []
        countries = country_repo.get_countries()
        for item in countries:
            rec_cities = []
            cities = city_repo.get_cities_by_country(item.id)
            for _item in cities:
                rec_cities.append(common.City(
                    city_id=_item.id,
                    city_name=_item.city_name
                ))
            rec_countries.append(
                common.Country(
                    country_id=item.id,
                    country_name=item.country_name,
                    city=rec_cities
                )
            )
        return common.ListCountry(records=rec_countries)
    except Exception:
        logger.error(f"list_common_types failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")