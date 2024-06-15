import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.factory.factory import RepositoryFactory as factory
from app.usecases.sync_helper import SyncHelper
from config.postgres import PostgresDB
from config.qdrant import QdrantVDB as qdrant
from config.weaviate import WeaviateVDB as weaviate
from constant import config
from pkg.logging import logger

from ..dto.admin import DeleteClassRequest, ManualSyncJobRequest
from .helper import combine_job_content

security = HTTPBasic()

async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = config.HTTP_ADMIN_USER_NAME
    correct_password = config.HTTP_ADMIN_PASSWORD
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong way",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

class AdminRouter:
    def __init__(self):
        self.agg_repo = factory.get_aggregate_repo()
        self.ai_helper = factory.get_ai_helper()
        self.qdrant_client = qdrant.setup_qdrant_connection()
        self.weaviate_client = weaviate.setup_weaviate_connection()
        self.sync_helper = SyncHelper(qdrant_client=self.qdrant_client, weaviate_client=self.weaviate_client)

        self.router = APIRouter(prefix="/admin/api", tags=['Admin'])
        self.router.add_api_route("/protected", self.protected_route, methods=["GET"])
        self.router.add_api_route("/weaviate/create-job-class", self.create_job_class, methods=["POST"])
        self.router.add_api_route("/weaviate/create-jobqna-class", self.create_jobqna_class, methods=["POST"])
        self.router.add_api_route("/weaviate/delete-class", self.delete_class, methods=["DELETE"])
        self.router.add_api_route("/manual-sync-job", self.manual_sync_job, methods=["POST"])

    async def protected_route(self, is_authenticated: bool = Depends(authenticate_user)):
        return {"message": "You are authorized to access this resource"}

    async def create_job_class(self, is_authenticated: bool = Depends(authenticate_user)):
        try:
            self.weaviate_client.collections.create_from_dict(weaviate.jobClass)
            return {"message": "Job class created successfully"}
        except Exception:
            logger.error(f"weaviate create_job_class failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def create_jobqna_class(self, is_authenticated: bool = Depends(authenticate_user)):
        try:
            self.weaviate_client.collections.create_from_dict(weaviate.jobQnAClass)
            return {"message": "JobQnA class created successfully"}
        except Exception:
            logger.error(f"weaviate create_jobqna_class failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def delete_class(self, payload: DeleteClassRequest, is_authenticated: bool = Depends(authenticate_user)):
        try:
            self.weaviate_client.collections.delete(payload.collection_name)
            return {"message": "Class deleted successfully"}
        except Exception:
            logger.error(f"weaviate delete_class failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
    async def manual_sync_job(self, req: ManualSyncJobRequest, is_authenticated: bool = Depends(authenticate_user), db: Session = Depends(PostgresDB.get_db)):
        try:
            for id in req.ids:
                job_agg = await self.agg_repo.get_job(db=db, id=id)
                
                # summarize content
                summarized_content = self.ai_helper.get_job_summarized(job_agg.content)

                acronyms_and_abbreviations = self.ai_helper.get_acronyms_and_abbreviation_of_job(job_agg.content)
                if isinstance(acronyms_and_abbreviations, list):
                    acronyms_and_abbreviations = ", ".join(acronyms_and_abbreviations)

                # combine content
                combined_content = combine_job_content(job_agg, summarized_content, acronyms_and_abbreviations)

                # vectorize the combined content
                vector = self.ai_helper.get_embedding(combined_content)

                job_agg.s_content = summarized_content
                job_agg.combined_content = combined_content

                await self.sync_helper.upsert_to_qdrant(config.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)

            return {"message": "Manual job sync completed successfully"}
        except Exception:
            logger.error(f"manual_sync_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

admin_router = AdminRouter().router
