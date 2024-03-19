from qdrant_client import QdrantClient
from qdrant_client.conversions import common_types as types
from qdrant_client.http.models import PointStruct
from app.repo.job_repo import JobRepository
from app.repo.resume_repo import ResumeRepository
from app.repo.aggregate import Aggregate
from app.ai.ai_helper import AI

import constant.config as constant
from constant.config import QDRANT_URL, QDRANT_INDEX_JOB_SEARCH, QDRANT_INDEX_RESUME_SEARCH


ai_helper = ai_helper = AI()

class SyncUsecase:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url="157.245.50.16",
            port=6333
        )
        self.agg_repo = Aggregate()

    def sync_job_to_qdrant(self, job_id):
        payload = self.agg_repo.get_job(job_id)

        # Summarize job description
        summarized_content = ai_helper.get_job_summarized(payload.content)
        
        # Embed summarized job description
        vector = ai_helper.get_embedding(summarized_content)
        
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
        # print(f"Synced job {job.id} to Qdrant")

    def sync_resume_to_qdrant(self, resume_id):
        payload = self.agg_repo.get_resume(resume_id)
        print(payload)

        # Summarize job description
        # summarized_content = ai_helper.get_job_summarized(payload.content)
        
        # Embed summarized job description
        # vector = ai_helper.get_embedding(summarized_content)
        # payload["vector"] = vector
        
        # FIXME: Fix upsert
        
        # points = [
        #     types.Points(
        #             # vector=vector[0],
        #             payloads=payload
        #         )
        #     ]
        # self.qdrant_client.upsert(
        #     collection_name=constant.QDRANT_INDEX_RESUME_SEARCH,
        #     points=points,
        # )

        # print(f"Synced job {job.id} to Qdrant")

