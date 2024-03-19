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

    def count_total_record(self, filter: Optional[models.Filter]) -> int:
        return self.client.count(
            collection_name=self.index_name,
            count_filter=filter,
            exact=True 
            # exact:
                # If `True` - provide the exact count of points matching the filter.
                # If `False` - provide the approximate count of points matching the filter. Works faster.
        )

    def list_jobs(self, input: Optional[job.ListJobRequest]) -> job.ListJobResponse:
        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        filter = models.Filter()

        if input.experience_level is not None:
            filter.must.append(
                models.FieldCondition(
                    key="experience_level",
                    match=models.MatchValue(
                        value=input.experience_level,
                    ),
                )
            )

        if input.type is not None:
            filter.must.append(
                models.FieldCondition(
                    key="job_type", # FIXME: fix this
                    match=models.MatchValue(
                        value=input.type
                    )
                )
            )

        if input.location is not None:
            filter.must.append(
                models.FieldCondition(
                    key="location", # FIXME: fix this
                    match=models.MatchValue(
                        value=input.location
                    )
                )
            )

        # FIXME: fix this
        if input.last_updated is not None:
            filter.must.append(
                models.FieldCondition(
                    key="updated_at",
                    range=models.Range(
                        gte=input.last_updated
                    )
                )
            )

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

        total_record = self.count_total_record(filter)

        hits = List[types.ScoredPoint]
        if input.vectors is not None:
            hits = self.client.search(
                collection_name=self.index_name,
                query_vector=input.vectors,
                query_filter=filter,
                offset=(input.page - 1) * input.size,
            )
        else:
            hits = self.client.scroll(
                collection_name=self.index_name,
                scroll_filter=filter,
                limit=input.size,
                offset=(input.page - 1) * input.size,
                order_by=models.OrderBy(
                    key="updated_at",
                    direction="desc"
                )
            )

        records = []
        for item in hits:
            score = item.score
            payload = item.payload

            job_record = job.JobAggregate(
                id= id,
                matching_score= score,
                title= payload["job_title"],
                content= payload["content"],
                content_url= payload["content_url"],
                is_hiring= payload["is_hiring"],
                opened_date= payload.get("opened_date"),
                closed_date= payload.get("closed_date"),
                salary_from= payload.get("salary_from"),
                salary_to= payload.get("salary_to"),
                job_type= payload.get("job_type"),
                company_type= payload.get("company_type"),
                created_at= payload.get("created_at"),
                updated_at= payload.get("updated_at"),
                user_id= payload.get("user_id"),  
                user_name= payload.get("user_name")
            )

            records.append(job_record)            

        return job.ListJobResponse(
            count=total_record,
            page=input.page,
            size=input.size,
            records=records
        )
