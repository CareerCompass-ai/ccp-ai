from typing import Optional

from config.es import ElasticSearchDB

from app.dto import job
from app.dto import mapper

class JobESRepository:
    def __init__(self, index_name: str):
        self.es_setup = ElasticSearchDB()
        self.client = self.es_setup.setup_elasticsearch_connection()
        self.index_name = index_name

    async def count_total_record(self, query: dict) -> int:
        response = await self.client.count(index=self.index_name, body={"query": query})
        return response["count"]

    async def list_jobs(self, input: Optional[job.ListJobRequest]) -> job.ListJobResponse:
        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10

        # Read the search strategies: https://coralogix.com/blog/42-elasticsearch-query-examples-hands-on-tutorial/
        
        # match strategy
        # query = {"match": {"content": input.input}} if input.input else {"match_all": {}}

        # query string strategy
        query = {
            "query_string": {
                "query": input.input if input.input else "*",
                "default_field": "content"  # Specify the field to search on
            }
        }
        
        response = await self.client.search(
            index=self.index_name,
            body={
                "query": query,
                "from": (input.page - 1) * input.size,
                "size": input.size,
            }
        )

        total_record = await self.count_total_record(query)

        records = []
        for hit in response["hits"]["hits"]:
            payload = hit["_source"]
            records.append(mapper.toJobDTO(payload))

        return job.ListJobResponse(
            count=total_record,
            page=input.page,
            size=input.size,
            records=records
        )
