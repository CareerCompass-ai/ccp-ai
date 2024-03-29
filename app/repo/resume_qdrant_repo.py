from typing import List, Optional

from qdrant_client.conversions import common_types as types
from qdrant_client.http import models
from config.qdrant import QdrantVDB

from app.dto import resume
from app.dto import mapper
from qdrant_client import QdrantClient
import constant.config as constant

class ResumeQdrantRepository:
    def __init__(self, index_name: str):
        self.qdrant_setup = QdrantVDB()
        # self.client = self.qdrant_setup.setup_qdrant_connection()
        self.index_name = index_name
        self.qdrant_client = QdrantClient(
            url=constant.DB_SERVER_IP,
            port=constant.QDRANT_PORT
        )
        
    def count_total_record(self, filter: Optional[models.Filter]) -> int:
        return self.qdrant_client.count(
            collection_name=self.index_name,
            count_filter=filter,
            exact=True
        )
    
    def list_resumes(self, input: Optional[resume.ListResumeRequest]) -> resume.ListResumeResponse:
        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        job_vector = self.qdrant_client.retrieve(
            collection_name="ccp_job_search",
            ids=[input.job_id],
            with_vectors=True,
        )

        filter = models.Filter()
        filter.must = []
        
        filter.must.append(
            models.FieldCondition(
                key="applied_jobs",
                match=models.MatchValue(value=input.job_id)
            )
        )
        total_record = self.count_total_record(filter).count

        records = []
        hits = List[types.ScoredPoint]
        hits = self.qdrant_client.search(
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