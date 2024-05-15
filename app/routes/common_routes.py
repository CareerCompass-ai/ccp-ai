from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app.dto import common

from app.repo.tag_repo import TagRepository 

from config.postgres import PostgresDB
import constant.common as constant

from pkg.logging import logger

common_router = APIRouter(
    prefix="/api",
    tags=['Common']
)

tag_repo = TagRepository()

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
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))