import json
import hashlib

from qdrant_client import QdrantClient
from qdrant_client.conversions import common_types as types
from qdrant_client.http.models import PointStruct

from elasticsearch import Elasticsearch

from app.repo.job_repo import JobRepository
from app.repo.resume_repo import ResumeRepository
from app.repo.aggregate import Aggregate

from app.ai.ai_helper import AI

import constant.config as constant

ai_helper = ai_helper = AI()

class SyncUsecase:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=constant.SERVER_IP,
            port=constant.QDRANT_PORT
        )

        self.es_client = Elasticsearch(
            constant.ES_URL, 
            basic_auth=[constant.ES_USERNAME, constant.ES_PASSWORD], 
        )

        self.agg_repo = Aggregate()

    def update_fields_qdrant(self, collection, id, payload):
        self.qdrant_client.set_payload(
            collection_name=collection,
            payload=payload,
            points=[id],
        )

    def upsert_to_qdrant(self, payload, vector):
        self.qdrant_client.upsert(
            collection_name=constant.QDRANT_INDEX_JOB_SEARCH,
            points= [ 
                PointStruct(
                    id=payload.id,
                    vector=vector.tolist(),
                    payload=payload.model_dump(),
                ),
            ]
        )

    def upsert_to_es(self, payload):
        self.es_client.index(
            index=constant.ES_INDEX_JOB_SEARCH,
            id=payload.id,
            body=payload.model_dump(),
        )

    def sync_job_to_qdrant_and_es(self, msg):
        payload = json.loads(msg.value())
        job_id = payload.get('after', {}).get('id')

        job_agg = self.agg_repo.get_job(job_id)

        if 'before' in payload and payload['before'] is not None:
            old_content = payload['before']['content']
            new_content = payload['after']['content']

            if hashlib.md5(old_content.encode()).hexdigest() != hashlib.md5(new_content.encode()).hexdigest():
                summarized_content = ai_helper.get_job_summarized(job_agg.content)
                vector = ai_helper.get_embedding(summarized_content)
                job_agg.s_content = summarized_content

                self.upsert_to_qdrant(job_agg, vector)
                self.upsert_to_es(job_agg)
            else:
                self.update_fields_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_id, job_agg.model_dump())
                self.upsert_to_es(job_agg)
        else:
            summarized_content = ai_helper.get_job_summarized(job_agg.content)
            vector = ai_helper.get_embedding(summarized_content)
            job_agg.s_content = summarized_content

            self.upsert_to_qdrant(job_agg, vector)
            self.upsert_to_es(job_agg)

    def sync_resume_to_qdrant(self, msg):
        payload = json.loads(msg.value())
        resume_id = payload.get('after', {}).get('id')

        resume_agg = self.agg_repo.get_resume(resume_id)

        # Summarize job description
        summarized_content = ai_helper.get_resume_summarized(resume_agg.content)
        
        # Embed summarized job description
        vector = ai_helper.get_embedding(summarized_content)

        resume_agg.s_content = summarized_content

        self.upsert_to_qdrant(resume_agg, vector)

    def sync_jobs_applied_resume_to_qdrant(self, msg):
        msg_dict = json.loads(msg.value())

        resume_id = msg_dict.get('after', {}).get('id')

        jobs_id_list = self.agg_repo.get_list_job_id(resume_id)
        
        payload={
                "applied_jobs": jobs_id_list,
        },

        self.update_fields_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_id, payload)