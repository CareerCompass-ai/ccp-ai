from qdrant_client import QdrantClient
from qdrant_client.conversions import common_types as types

from app.repo.job_repo import JobRepository
from app.ai.ai_helper import AI

import constant.config as constant

ai_helper = ai_helper = AI()

class SyncUsecase:
    def __init__(self):
        self.job_repo = JobRepository()
        self.qdrant_client = QdrantClient()

    def sync_job_to_qdrant(self, job_id):
        job = self.job_repo.get_by_id(job_id)
        if job is None:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Aggregate data for Qdrant insertion
        # TODO: get data aggregation

        # Summarize job description
        summarized_content = ai_helper.get_job_summarized(job.content)
        
        # Embed summarized job description
        vectors = ai_helper.get_embedding(summarized_content)
        
        # FIXME: Fix upsert
        metadata = {"id": job.id, "vectors": vectors}  
        
        points = [types.Points(vector=vectors[0], metadata=metadata)]
        self.qdrant_client.upsert(
            collection_name=constant.QDRANT_INDEX_JOB_SEARCH,
            points=points,
        )

        print(f"Synced job {job.id} to Qdrant")

