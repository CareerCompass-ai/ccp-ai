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

    def get_job(self, input: Optional[job.GetJobRequest]) -> job.JobAggregate:
        if input.id is not None:
            record = self.client.retrieve(
                self.index_name,
                ids=[input.id]
            )[0]

            if record is None:
                return None

            result = job.JobAggregate(
                id=record.id,
                job_title=record.payload["job_title"],
                content= record.payload["content"],
                s_content= record.payload["s_content"],
                content_url= record.payload["content_url"],
                is_hiring= record.payload["is_hiring"],
                opened_date= record.payload["opened_date"],
                closed_date= record.payload["closed_date"],
                salary_from= record.payload["salary_from"],
                salary_to= record.payload["salary_to"],
                job_type= record.payload["job_type"],
                company_type= record.payload["company_type"],
                created_at= record.payload["created_at"],
                updated_at= record.payload["updated_at"],
                recruiter_id= record.payload["recruiter_id"],  
                recruiter_name= record.payload["recruiter_name"],
                job_tags= record.payload["job_tags"],
                address= record.payload["address"],
                hiring_level= record.payload["hiring_level"],
            )

            return result

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
        if filter.must is None:
            filter.must = []
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

        total_record = self.count_total_record(filter).count

        records = []
        hits = List[types.ScoredPoint]
        if input.vectors is not None:
            hits = self.client.search(
                collection_name=self.index_name,
                query_vector=input.vectors,
                query_filter=filter,
                offset=(input.page - 1) * input.size,
            )

            for item in hits:
                score = item.score
                payload = item.payload

                job_record = job.JobAggregate(
                    id= item.id,
                    matching_score= score,
                    job_title= payload["job_title"],
                    content= payload["content"],
                    s_content= payload["s_content"],
                    content_url= payload["content_url"],
                    is_hiring= payload["is_hiring"],
                    opened_date= payload["opened_date"],
                    closed_date= payload["closed_date"],
                    salary_from= payload["salary_from"],
                    salary_to= payload["salary_to"],
                    job_type= payload["job_type"],
                    company_type= payload["company_type"],
                    created_at= payload["created_at"],
                    updated_at= payload["updated_at"],
                    recruiter_id= payload["recruiter_id"],  
                    recruiter_name= payload["recruiter_name"],
                    job_tags= payload["job_tags"],
                    address= payload["address"],
                )

                del payload
                records.append(job_record)  
        else:
            hits = self.client.scroll(
                collection_name=self.index_name,
                scroll_filter=filter,
                limit=input.size,
                # offset=(input.page - 1) * input.size,
                # start_from=(input.page - 1) * input.size,
                order_by=models.OrderBy(
                    key="updated_at",
                    direction="desc"
                ),
                with_payload=True
                # with_vectors=False
            )
            for item in hits[0]:
                if item is not None:
                    payload = item.payload

                    job_record = job.JobAggregate(
                        id= item.id,
                        job_title= payload["job_title"],
                        content= payload["content"],
                        s_content= payload["s_content"],
                        content_url= payload["content_url"],
                        is_hiring= payload["is_hiring"],
                        opened_date= payload["opened_date"],
                        closed_date= payload["closed_date"],
                        salary_from= payload["salary_from"],
                        salary_to= payload["salary_to"],
                        job_type= payload["job_type"],
                        company_type= payload["company_type"],
                        created_at= payload["created_at"],
                        updated_at= payload["updated_at"],
                        recruiter_id= payload["recruiter_id"],  
                        recruiter_name= payload["recruiter_name"],
                        job_tags= payload["job_tags"],
                        address= payload["address"],
                    )

                    del payload
                    records.append(job_record)  

        return job.ListJobResponse(
            count=total_record,
            page=input.page,
            size=input.size,
            records=records
        )
