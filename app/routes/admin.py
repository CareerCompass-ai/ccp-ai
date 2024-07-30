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

from ..dto.admin import DeleteClassRequest, ManualSyncJobRequest, ManualSyncResumeRequest, ManualCreateSearchSuggestion
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
        self.redis_repo = factory.get_redis_repo()
        self.qdrant_client = qdrant.setup_qdrant_connection()
        self.weaviate_client = weaviate.setup_weaviate_connection()
        self.sync_helper = SyncHelper(qdrant_client=self.qdrant_client, weaviate_client=self.weaviate_client)

        self.router = APIRouter(prefix="/api/admin", tags=['Admin'])
        self.router.add_api_route("/protected", self.protected_route, methods=["GET"])
        self.router.add_api_route("/weaviate/create-job-class", self.create_job_class, methods=["POST"])
        self.router.add_api_route("/weaviate/create-jobqna-class", self.create_jobqna_class, methods=["POST"])
        self.router.add_api_route("/weaviate/delete-class", self.delete_class, methods=["DELETE"])
        self.router.add_api_route("/manual-sync-jobs", self.manual_sync_jobs, methods=["POST"])
        self.router.add_api_route("/manual-sync-resumes", self.manual_sync_resumes, methods=["POST"])
        self.router.add_api_route("/manual-add-search-suggestion", self.create_search_suggestion, methods=["POST"])

    async def create_search_suggestion(self, req: ManualCreateSearchSuggestion):
        try:
            pattern = f"search_suggestion"
            for value in req.data:
                self.redis_repo.sadd(pattern=pattern, value=value)
            return {"message": "success"}
        except Exception:
            logger.error(f"create_search_suggestion failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
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
        
    async def manual_sync_jobs(self, req: ManualSyncJobRequest, is_authenticated: bool = Depends(authenticate_user), db: Session = Depends(PostgresDB.get_db)):
        try:
            for id in req.ids:
                job_agg = await self.agg_repo.get_job(db=db, id=id)
                
                # summarize content
                summarized_content = await self.ai_helper.get_job_summarized(job_agg.content)

                tmp_content = job_agg.content + "; Job title: " + job_agg.job_title
                acronyms_and_abbreviations = await self.ai_helper.get_acronyms_and_abbreviation_of_job(tmp_content)
                if isinstance(acronyms_and_abbreviations, list):
                    acronyms_and_abbreviations = ", ".join(acronyms_and_abbreviations)

                # combine content
                combined_content = await combine_job_content(job_agg, summarized_content, acronyms_and_abbreviations)

                # vectorize the combined content
                vector = await self.ai_helper.get_embedding(combined_content)

                job_agg.s_content = summarized_content
                job_agg.combined_content = combined_content

                await self.sync_helper.upsert_to_qdrant(config.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)

            return {"message": "Manual sync jobs completed successfully"}
        except Exception:
            logger.error(f"manual_sync_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
    async def manual_sync_resumes(self, req: ManualSyncResumeRequest, is_authenticated: bool = Depends(authenticate_user), db: Session = Depends(PostgresDB.get_db)):
        try:
            for id in req.ids:
                resume_agg = await self.agg_repo.get_resume(db=db, id=id)

                summarized_content = await self.ai_helper.get_resume_summarized(resume_agg.content)

                # TODO: skills_and_knowledge = LLM Get skills and knowledge from resume
                skills_and_knowledge = await self.ai_helper.get_skills_and_knowledge_of_resume(resume_agg.content)
                if isinstance(skills_and_knowledge, list):
                    skills_and_knowledge = ", ".join(skills_and_knowledge)
                
                # combined_content = summarized_content + resume_agg.resume_name + skills_and_knowledge

                # predict candidate's level
                level = await self.ai_helper.get_candidate_level(resume_agg.content)
                if isinstance(level, list):
                    level = ", ".join(level)

                # predict candidate's major
                tmp_content = summarized_content + "; Skills and knowledges: " + skills_and_knowledge + "; Level: " + level
                major = await self.ai_helper.get_candidate_major(tmp_content)
                if isinstance(major, list):
                    major = ", ".join(major)

                # combine content
                combined_content = summarized_content + ", " + skills_and_knowledge + ", " + level + ", " + major

                # vectorize the combined content
                vector = await self.ai_helper.get_embedding(combined_content)

                resume_agg.s_content = summarized_content
                resume_agg.combined_content = combined_content

                await self.sync_helper.upsert_to_qdrant(config.QDRANT_INDEX_RESUME_SEARCH, resume_agg, vector)

            return {"message": "Manual sync resumes completed successfully"}
        except Exception:
            logger.error(f"manual_sync_resume failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

admin_router = AdminRouter().router
