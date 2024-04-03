from fastapi import status, HTTPException, Depends, APIRouter

from app.dto import common

from app.repo.tag_repo import TagRepository 

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
            tags=tags
        )

        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))