import ssl

from qdrant_client import QdrantClient
from qdrant_client.conversions import common_types as types
from qdrant_client.http.models import PointStruct

from elasticsearch import Elasticsearch

from app.repo.job_repo import JobRepository
from app.repo.resume_repo import ResumeRepository
from app.repo.aggregate import Aggregate

from app.ai.ai_helper import AI

import constant.config as constant


ai_helper = ai_helper = AI()

class SyncUsecase:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=constant.SERVER_IP,
            port=constant.QDRANT_PORT
        )

        self.es_client = Elasticsearch(
            constant.ES_URL, 
            basic_auth=[constant.ES_USERNAME, constant.ES_PASSWORD], 
        )

        self.agg_repo = Aggregate()

    def sync_job_to_qdrant_and_es(self, job_id):
        payload = self.agg_repo.get_job(job_id)

        # Summarize job description
        summarized_content = ai_helper.get_job_summarized(payload.content)
        
        # Embed summarized job description
        vector = ai_helper.get_embedding(summarized_content)
        payload.s_content = summarized_content
        
        # Upsert to qdrant collection
        self.qdrant_client.upsert(
            collection_name=constant.QDRANT_INDEX_JOB_SEARCH,
            points= [ 
                PointStruct(
                    id=payload.id,
                    vector=vector.tolist(),
                    payload=payload.model_dump(),
                ),
            ]
        )

        # Create or update a document in ES index
        self.es_client.index(
            index=constant.ES_INDEX_JOB_SEARCH,
            id=payload.id,
            body=payload.model_dump(),
        )
        # print(f"Synced job {job.id} to Qdrant")

    def sync_resume_to_qdrant(self, resume_id):
        payload = self.agg_repo.get_resume(resume_id)

        # Summarize job description
        summarized_content = ai_helper.get_resume_summarized(payload.content)
        
        # Embed summarized job description
        vector = ai_helper.get_embedding(summarized_content)

        payload.s_content = summarized_content
        
        self.qdrant_client.upsert(
            collection_name=constant.QDRANT_INDEX_RESUME_SEARCH,
            points= [ 
                PointStruct(
                    id=payload.id,
                    vector=vector.tolist(),
                    payload=payload.model_dump(),
                ),
            ]
        )

    def sync_jobs_applied_resume_to_qdrant(self, resume_id):
        jobs_id_list = self.agg_repo.get_list_job_id(resume_id)
        self.qdrant_client.set_payload(
            collection_name=constant.QDRANT_INDEX_RESUME_SEARCH,
            payload={
                "applied_jobs": jobs_id_list,
            },
            points=[resume_id],
        )