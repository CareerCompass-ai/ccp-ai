from qdrant_client import QdrantClient
from qdrant_client.conversions import common_types as types

from app.repo.job_repo import JobRepository
from app.repo.aggregate import Aggregate as agg_repo
from app.ai.ai_helper import AI

import constant.config as constant

ai_helper = ai_helper = AI()

class SyncUsecase:
    def __init__(self):
        self.job_repo = JobRepository()
        self.qdrant_client = QdrantClient()

    def sync_job_to_qdrant(self, job_id):
        payload = agg_repo.get_job(job_id)

        # Summarize job description
        # summarized_content = ai_helper.get_job_summarized(payload.content)
        
        # Embed summarized job description
        # vector = ai_helper.get_embedding(summarized_content)
        # payload["vector"] = vector
        
        # FIXME: Fix upsert
        
        points = [
            types.Points(
                    # vector=vector[0],
                    payloads=payload
                )
            ]
        self.qdrant_client.upsert(
            collection_name=constant.QDRANT_INDEX_JOB_SEARCH,
            points=points,
        )

        # print(f"Synced job {job.id} to Qdrant")

