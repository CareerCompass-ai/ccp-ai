from typing import Optional

from config.weaviate import WeaviateVDB

from app.dto import job
from app.dto import mapper

class JobWeaviateRepository:
    def __init__(self, collection_name: str):
        self.weaviate_setup = WeaviateVDB()
        self.client = self.weaviate_setup.setup_weaviate_connection()
        self.collection_name = collection_name

    def list_jobs(self, input: job.ListJobRequest) -> job.ListJobResponse:
        job_collection = self.client.collections.get(self.collection_name)

        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        res = job_collection.query.hybrid(
            query=input.input,
            alpha=input.alpha,
            limit=input.size
        )

        records = []
        for o in res.objects:
            records.append(mapper.toJobWeaviateDTO(o))

        return job.ListJobResponse(
            count=len(records), # FIXME: count total record by input and filters
            page=1,
            size=100,
            records=records
        )
