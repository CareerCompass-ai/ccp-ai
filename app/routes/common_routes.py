from fastapi import status, HTTPException, APIRouter, Depends
import traceback

from app.dto import common

from app.repo.tag_repo import TagRepository 
from app.repo.country_repo import CountryRepository
from app.repo.city_repo import CityRepository

from config.postgres import PostgresDB
from sqlalchemy.orm import Session

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
async def list_common_types(
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        tags = await tag_repo.list_tag(db=db)

        rec_countries = []

        countries = await country_repo.get_countries(db=db)
        list_countries = []
        for item in countries:
            list_countries.append (
                common.ListCountry (
                    country_id=item.id,
                    country_name=item.country_name
                )
            )
            rec_cities = []
            cities = await city_repo.get_cities_by_country(db=db, country_id=item.id)
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

        data = common.ListCommonTypes(
            tag=tags,
            hiring_level=constant.HIRING_LEVELS,
            job_type=constant.JOB_TYPES,
            company_type=constant.COMPANY_TYPES,
            work_place=constant.WORK_PLACES,
            countries=list_countries,
            cities=rec_countries
        )
        return data
    except Exception:
        logger.error(f"list_common_types failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))