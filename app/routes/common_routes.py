from fastapi import status, HTTPException, Depends, APIRouter

from app.dto import common

from app.repo.tag_repo import TagRepository 

import constant.common as constant

common_router = APIRouter(
    prefix="/api",
    tags=['Common']
)

tag_repo = TagRepository()

@common_router.get("/common/types", response_model=common.ListCommonTypes)
def list_common_types():
    try:
        tags = tag_repo.list_tag()

        data = common.ListCommonTypes(
            tags=tags,
            hiring_levels=constant.HIRING_LEVELS,
            job_types=constant.JOB_TYPES,
            company_types=constant.COMPANY_TPYES,
            work_places=constant.WORK_PLACE,
        )

        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))