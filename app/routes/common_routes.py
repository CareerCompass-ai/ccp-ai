import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import constant.common as constant
from app.dto import common
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from pkg.logging import logger


class CommonRouter:
    def __init__(self):
        self.tag_repo = factory.get_tag_repo()
        self.country_repo = factory.get_country_repo()
        self.city_repo = factory.get_city_repo()
        self.router = APIRouter(prefix="/api", tags=['Common'])
        self.router.add_api_route("/common/types", self.list_common_types, methods=["GET"], response_model=common.ListCommonTypes)

    async def list_common_types(self, db: Session = Depends(PostgresDB.get_db)):
        try:
            tags = await self.tag_repo.list_tag(db=db)

            rec_countries = []

            countries = await self.country_repo.get_countries(db=db)
            list_countries = []
            for item in countries:
                list_countries.append(
                    common.ListCountry(
                        country_id=item.id,
                        country_name=item.country_name
                    )
                )
                rec_cities = []
                cities = await self.city_repo.get_cities_by_country(db=db, country_id=item.id)
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


common_router = CommonRouter().router
