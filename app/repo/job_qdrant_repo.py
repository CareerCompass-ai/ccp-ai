from typing import List, Optional

from qdrant_client.conversions import common_types as types
from qdrant_client.http import models
from config.qdrant import QdrantVDB

from app.dto import job

class JobQdrantRepository:
    def __init__(self, index_name: str):
        self.qdrant_setup = QdrantVDB()
        self.client = self.qdrant_setup.setup_qdrant_connection()
        self.index_name = index_name

    def list_jobs(self, input: Optional[job.ListJobRequest]) -> List[int]:
        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        filter = models.Filter()

        if input.salary_from is not None:
            filter.must.append(
                models.FieldCondition(
                    key="salary_from",
                    range=models.Range(
                        gte=input.salary_from
                    )
                )
            )

        if input.salary_to is not None:
            filter.must.append(
                models.FieldCondition(
                    key="salary_to",
                    range=models.Range(
                        lte=input.salary_to
                    )
                )
            )

        if input.experience_level is not None:
            filter.must.append(
                models.FieldCondition(
                    key="experience_level",
                    match=models.MatchValue(
                        value=input.experience_level,
                    ),
                )
            )

        results = List[types.ScoredPoint]
        if input.vectors is not None:
            results = self.client.search(
                collection_name=self.index_name,
                query_vector=input.input,
                query_filter=filter,
                offset=(input.page - 1) * input.size,
            ) 
        else:
            # FIXME: handle this case
            results = self.client.scroll(
                collection_name=self.index_name,
                scroll_filter=filter,
                limit=input.size,
            )

        job_ids = [result.id for result in results]
        return job_ids
