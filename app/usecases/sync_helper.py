import json
import constant

from qdrant_client import QdrantClient
# from elasticsearch import Elasticsearch

from qdrant_client.http.models import PointStruct

class SyncHelper:
    def __init__(self, qdrant_client: QdrantClient, es_client):
        self.qdrant_client = qdrant_client
        # self.es_client = es_client

    def update_fields_qdrant(self, collection_name: str, id: int, payload):
        self.qdrant_client.set_payload(
            collection_name=collection_name,
            payload=payload,
            points=[id],
        )

    def upsert_to_qdrant(self, collection_name: str, payload, vector):
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

    # def upsert_to_es(self, index: str, payload):
    #     self.es_client.index(
    #         index=index,
    #         id=payload.id,
    #         body=payload.model_dump(),
    #     )
