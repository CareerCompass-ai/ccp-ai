import traceback

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

import constant.common as constant
from app.dto import common
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from pkg.logging import logger
from typing import Optional
class CommonRouter:
    def __init__(self):
        self.tag_repo = factory.get_tag_repo()
        self.country_repo = factory.get_country_repo()
        self.city_repo = factory.get_city_repo()
        self.redis_repo = factory.get_redis_repo()

        self.router = APIRouter(prefix="/api", tags=['Common'])
        self.router.add_api_route("/common/types", self.list_common_types, methods=["GET"], response_model=common.ListCommonTypes)
        self.router.add_api_route("/v2/common/types", self.list_common_types_v2, methods=["GET"], response_model=common.ListCommonTypesv2)
        self.router.add_api_route("/common/search-suggestion", self.list_search_suggestion, methods=["GET"])
        self.router.add_api_route("/common/search-suggestion", self.delete_search_suggestions, methods=["DELETE"])

    async def delete_search_suggestions(self, req: common.DeleteSearchSuggestions):
        try:
            pattern = "search_suggestion"
            for value in req.keys:
                self.redis_repo.srem(pattern, value)
        except Exception:
            logger.error(f"delete_search_suggestions failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

    async def list_search_suggestion(self):
        try:
            pattern = f"search_suggestion"
            keys = self.redis_repo.smembers(pattern=pattern)
            sorted_keys = sorted(keys)
            return sorted_keys
        except Exception:
            logger.error(f"list_search_suggestion failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
    def get_value_from_constant(self, record) -> list[common.CommonTypev2]:
        records = []
        for item in record:
            records.append(
                common.CommonTypev2(
                    name=item
                )
            )
        return records

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

    async def list_common_types_v2(self, db: Session = Depends(PostgresDB.get_db)):
        try:
            tags = await self.tag_repo.list_tag_v2(db=db)
            rec_tags = []
            for item in tags:
                rec_tags.append(
                    common.CommonTypev2(
                        name=item.tag_name
                    )
                )

            countries = await self.country_repo.get_countries_v2(db=db)
            rec_countries = []
            for item in countries:
                rec_countries.append(
                    common.CommonTypev2(
                        name=item.country_name
                    )
                )

            cities = await self.city_repo.get_cities(db=db)
            rec_cities = []
            for _item in cities:
                rec_cities.append(common.CommonTypev2(
                        name=_item.city_name
                    )
                )

            rec_common_job_titles = self.get_value_from_constant(constant.COMMON_JOB_TITLES)
            rec_hiring_levels = self.get_value_from_constant(constant.HIRING_LEVELS)
            rec_job_types = self.get_value_from_constant(constant.JOB_TYPES)
            rec_company_types = self.get_value_from_constant(constant.COMPANY_TYPES)
            rec_work_places = self.get_value_from_constant(constant.WORK_PLACES)

            data = common.ListCommonTypesv2(
                job_tags=rec_tags,
                roles=rec_common_job_titles,
                hiring_levels=rec_hiring_levels,
                job_types=rec_job_types,
                company_types=rec_company_types,
                work_places=rec_work_places,
                countries=rec_countries,
                cities=rec_cities,
            )
            return data
        except Exception:
            logger.error(f"list_common_types failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
common_router = CommonRouter().router
