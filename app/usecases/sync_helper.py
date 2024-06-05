from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from weaviate import WeaviateClient
from weaviate.classes.query import Filter

# from elasticsearch import Elasticsearch


class SyncHelper:
    def __init__(self, qdrant_client: QdrantClient, weaviate_client: WeaviateClient):
        self.qdrant_client = qdrant_client
        self.weaviate_client = weaviate_client
        # self.es_client = es_client

    async def update_fields_qdrant(self, collection_name: str, id: int, payload):
        self.qdrant_client.set_payload(
            collection_name=collection_name,
            payload=payload,
            points=[id],
        )

    async def upsert_to_qdrant(self, collection_name: str, payload, vector):
        self.qdrant_client.upsert(
            collection_name=collection_name,
            points=[ 
                PointStruct(
                    id=payload.id,
                    vector=vector.tolist(),
                    payload=payload.model_dump(),
                ),
            ]
        )

    async def insert_to_weaviate(self, class_name: str, payload):
        collection = self.weaviate_client.collections.get(class_name)

        properties = payload.model_dump()
        properties.pop('id', None)
        properties["job_id"]=payload.id

        collection.data.insert(
            properties=properties,
            # references={
            #     "hasCategory": str(payload.id)
            # }
        )

    async def replace_object_weaviate(self, class_name: str, payload):
        collection = self.weaviate_client.collections.get(class_name)

        properties = payload.model_dump()
        record = collection.query.fetch_objects(
            filters=Filter.by_property("job_id").equal(payload.id)
        )

        properties.pop('id', None)
        properties["job_id"]=payload.id
        collection.data.replace(record.objects[0].uuid, properties=properties)

    async def update_object_properties_weaviate(self, class_name: str, payload):
        collection = self.weaviate_client.collections.get(class_name)

        properties = payload.model_dump()
        record = collection.query.fetch_objects(
            filters=Filter.by_property("job_id").equal(properties.id)
        )

        properties.pop('id', None)
        properties["job_id"]=payload.id
        collection.data.update(record.objects[0].uuid, properties=properties)

    # def update_object_weaviate(self, class_name: str):
    #     self.weaviate_client


    # def upsert_to_es(self, index: str, payload):
    #     self.es_client.index(
    #         index=index,
    #         id=payload.id,
    #         body=payload.model_dump(),
    #     )
