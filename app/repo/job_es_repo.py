from typing import List, Optional

from config.es import ElasticSearchDB

from app.dto import job
from app.dto import mapper

class JobESRepository:
    def __init__(self, index_name: str):
        self.es_setup = ElasticSearchDB()
        self.client = self.es_setup.setup_elasticsearch_connection()
        self.index_name = index_name


    def count_total_record(self, filter: Optional[str]) -> int:
        return self.client.count(
            index=self.index_name,
        )

    def list_jobs(self, input: Optional[job.ListJobRequest]) -> job.ListJobResponse:
        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        if input.input is not None:
            # TODO: handle full-text search with input on field "content" in ES
            pass


        total_record = self.count_total_record(filter).count

    #     records = []
    #     hits = List[types.ScoredPoint]
    #     if input.vectors is not None:
    #         hits = self.client.search(
    #             collection_name=self.index_name,
    #             query_vector=input.vectors,
    #             query_filter=filter,
    #             offset=(input.page - 1) * input.size,
    #         )

    #         for item in hits:
    #             score = item.score
    #             payload = item.payload

    #             result = mapper.toJobDTO(payload)
    #             result.matching_score = score

    #             records.append(result)  
    #     else:
    #         hits = self.client.scroll(
    #             collection_name=self.index_name,
    #             scroll_filter=filter,
    #             limit=input.size,
    #             # offset=(input.page - 1) * input.size,
    #             # start_from=(input.page - 1) * input.size,
    #             order_by=models.OrderBy(
    #                 key="updated_at",
    #                 direction="desc"
    #             ),
    #             with_payload=True
    #             # with_vectors=False
    #         )
    #         for item in hits[0]:
    #             if item is not None:
    #                 payload = item.payload

    #                 records.append(mapper.toJobDTO(payload))   

    #     return job.ListJobResponse(
    #         count=total_record,
    #         page=input.page,
    #         size=input.size,
    #         records=records
    #     )
