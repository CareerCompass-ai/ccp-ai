from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.ai.ai_helper import AI
from constant import config
from ..dto.admin import DeleteClassRequest, ManualSyncJobRequest
from app.usecases.sync_helper import SyncHelper

from app.repo.aggregate import Aggregate

from config.weaviate import WeaviateVDB as weaviate
from config.qdrant import QdrantVDB as qdrant

from pkg.logging import logger


admin_router = APIRouter(
    prefix="/admin/api",
    tags=['Admin']
)

security = HTTPBasic()

agg_repo = Aggregate()
ai_helper = AI()
qdrant_client = qdrant.setup_qdrant_connection()
weaviate_client = weaviate.setup_weaviate_connection()
sync_helper = SyncHelper(qdrant_client=qdrant_client, weaviate_client=weaviate_client)

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = config.HTTP_ADMIN_USER_NAME
    correct_password = config.HTTP_ADMIN_PASSWORD
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong way",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@admin_router.get("/protected")
async def protected_route(is_authenticated: bool = Depends(authenticate_user)):
    return {"message": "You are authorized to access this resource"}

@admin_router.post("/weaviate/create-job-class")
async def create_job_class(is_authenticated: bool = Depends(authenticate_user)):
    client = weaviate.setup_weaviate_connection()

    try:
        # client.schema.create_from_config(weaviate.jobClass)
        # client.collections.create(
        #     "Job",
        #     "Job collection",
        # )
        client.collections.create_from_dict(weaviate.jobClass)
        return {"message": "Job class created successfully"}
    except Exception as e:
        logger.error(f"weaviate create_job_class failed error = {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@admin_router.post("/weaviate/create-jobqna-class")
async def create_job_class(is_authenticated: bool = Depends(authenticate_user)):
    client = weaviate.setup_weaviate_connection()

    try:
        client.collections.create_from_dict(weaviate.jobQnAClass)
        return {"message": "JobQnA class created successfully"}
    except Exception as e:
        logger.error(f"weaviate create_job_class failed error = {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@admin_router.delete("/weaviate/class")
async def delete_class(payload: DeleteClassRequest, is_authenticated: bool = Depends(authenticate_user)):
    client = weaviate.setup_weaviate_connection()

    try:
        client.collections.delete(payload.collection_name)
        return {"message": "JobQnA class created successfully"}
    except Exception as e:
        logger.error(f"weaviate delete_job_class failed error = {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@admin_router.post("/manual-sync-job")
async def manual_sync_job(req: ManualSyncJobRequest, is_authenticated: bool = Depends(authenticate_user)):
    try:
        for id in req.ids:
            job_agg = agg_repo.get_job(id)
            summarized_content = ai_helper.get_job_summarized(job_agg.content)
            vector = ai_helper.get_embedding(summarized_content)
            job_agg.s_content = summarized_content
            
            sync_helper.upsert_to_qdrant(config.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)

        return {"message": "ok"}
    except Exception as e:
        logger.error(f"manual-sync-job failed error = {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    