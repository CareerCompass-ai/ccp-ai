from typing import List, Optional

from qdrant_client.conversions import common_types as types
from qdrant_client.http import models
from config.qdrant import QdrantVDB

from app.dto import job
from app.dto import mapper

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

            return mapper.toJobDTO(record.payload)

    def count_total_record(self, filter: Optional[models.Filter]) -> int:
        return self.client.count(
            collection_name=self.index_name,
            count_filter=filter,
            exact=True 
            # exact:
                # If `True` - provide the exact count of points matching the filter.
                # If `False` - provide the approximate count of points matching the filter. Works faster.
        )

    # TODO: find threshold to decide return or not return || base on score -> return label ? relavent or not, not return
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
        if filter.should is None:
            filter.should = []
        if filter.must_not is None:
            filter.must_not = []

        # TODO: handle this case
        if input.job_tags is not None :
            pass

        if input.hiring_level is not None:
            input.hiring_level = input.hiring_level[0].split(',')

            for level in input.hiring_level:
                filter.should.append(
                        models.FieldCondition(
                            key="hiring_level",
                            match=models.MatchValue(
                                value=level,
                            ),
                        )
                    )

        if input.job_type is not None:
            input.job_type = input.job_type.split(',')
            for job_type in input.job_type:
                filter.should.append(
                    models.FieldCondition(
                        key="job_type",
                        match=models.MatchValue(
                            value=job_type,
                        ),
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
        

        if input.company_type is not None:
            input.company_type = input.company_type.split(',')

            for type in input.company_type:
                filter.should.append(
                    models.FieldCondition(
                        key="company_type",
                        match=models.MatchValue(
                            value=type,
                        ),
                    )
                )

        # FIXME: fix this
        if input.last_updated is not None:
            filter.must.append(
                models.FieldCondition(
                    key="updated_at",
                    range=models.Range(
                        lte=input.last_updated
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

        if input.work_place is not None:
            input.work_place = input.work_place[0].split(',')
            for level in input.work_place:
                filter.should.append(
                        models.FieldCondition(
                            key="work_place",
                            match=models.MatchValue(
                                value=level,
                            ),
                        )
                    )
                
        if input.city_name is not None:
            for type in input.city_name:
                filter.should.append(
                    models.FieldCondition(
                        key="city_name",
                        match=models.MatchValue(
                            value=type,
                        ),
                    )
                )

        if input.country_name is not None:
            for type in input.country_name:
                filter.should.append(
                    models.FieldCondition(
                        key="country_name",
                        match=models.MatchValue(
                            value=type,
                        ),
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

                result = mapper.toJobDTO(payload)
                result.matching_score = score

                records.append(result)  
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

                    records.append(mapper.toJobDTO(payload))   

        return job.ListJobResponse(
            count=total_record,
            page=input.page,
            size=input.size,
            records=records
        )
