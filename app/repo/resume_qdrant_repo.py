from typing import List, Optional

from qdrant_client.conversions import common_types as types
from qdrant_client.http import models

import constant.config as constant
from app.dto import mapper, resume, recruiter
from config.qdrant import QdrantVDB
from pkg.logging import logger


class ResumeQdrantRepository:
    def __init__(self, index_name: str):
        self.qdrant_setup = QdrantVDB()
        self.client = self.qdrant_setup.setup_qdrant_connection()
        self.index_name = index_name
        
    async def count_total_record(self, filter: Optional[models.Filter]) -> int:
        return self.client.count(
            collection_name=self.index_name,
            count_filter=filter,
            exact=True
        )
    
    async def get_resume_vector(self, resume_id: str) -> list[float]:
        data = self.client.retrieve(
            collection_name=self.index_name,
            ids=[resume_id],
            with_vectors=True,
        )

        if not data:
            return []
        
        return data[0].vector
    
    async def list_resumes_by_ids(self, resume_ids: list[int]):
        data = self.client.retrieve(
            collection_name=self.index_name,
            ids=resume_ids,
            with_payload=True,
            with_vectors=False
        )
        records = []
        for item in data:
            payload = item.payload

            result = mapper.toResumeDTO(payload)

            records.append(result)

        return records

    async def list_resumes(self, input: Optional[resume.ListResumeRequest]) -> resume.ListResumeResponse:
        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        # TODO: Move this to above layer and call from job qdran repo, then pass the vector here
        job_vector = self.client.retrieve(
            collection_name=constant.QDRANT_INDEX_JOB_SEARCH,
            ids=[input.job_id],
            with_vectors=True,
        )

        if not job_vector:
            # If job_vector is empty, return an empty response
            logger.info(f"No vectors found for job_id: {input.job_id}")
            return resume.ListResumeResponse(
                count=0,
                page=input.page,
                size=input.size,
                records=[]
            )

        filter = models.Filter()
        filter.must = []
        
        filter.must.append(
            models.FieldCondition(
                key="applied_jobs",
                match=models.MatchValue(value=input.job_id)
            )
        )
        _res = await self.count_total_record(filter)
        total_record = _res.count

        records = []
        hits = List[types.ScoredPoint]
        hits = self.client.search(
            collection_name=self.index_name,
            query_vector=job_vector[0].vector,
            query_filter=filter,
            offset=(input.page - 1) * input.size,
        )
        for item in hits:
            score = item.score
            payload = item.payload

            result = mapper.toResumeDTO(payload)
            result.matching_score = score

            records.append(result)

        return resume.ListResumeResponse(
            count=total_record,
            page=input.page,
            size=input.size,
            records=records
        )