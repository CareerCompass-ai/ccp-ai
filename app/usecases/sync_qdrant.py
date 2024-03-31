import json
import hashlib

from qdrant_client import QdrantClient

from elasticsearch import Elasticsearch

from app.repo.aggregate import Aggregate

from app.ai.ai_helper import AI
from .sync_helper import SyncHelper

import constant.config as constant

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

        self.ai_helper = AI()
        self.sync_helper = SyncHelper(qdrant_client=self.qdrant_client, es_client=self.es_client)

        self.agg_repo = Aggregate()

    def sync_job_to_qdrant_and_es(self, msg):
        payload = dict(json.loads(msg.value()))
        job_id = dict(payload.get('after', {})).get('id')

        job_agg = self.agg_repo.get_job(job_id)

        if 'before' in payload and payload['before'] is not None:
            old_content = str(payload['before']['content'])
            new_content = str(payload['after']['content'])

            if hashlib.md5(old_content.encode()).hexdigest() != hashlib.md5(new_content.encode()).hexdigest():
                summarized_content = self.ai_helper.get_job_summarized(job_agg.content)
                vector = self.ai_helper.get_embedding(summarized_content)
                job_agg.s_content = summarized_content

                self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)
                self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)
            else:
                self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_id, job_agg.model_dump())
                self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)
        else:
            summarized_content = self.ai_helper.get_job_summarized(job_agg.content)
            vector = self.ai_helper.get_embedding(summarized_content)
            job_agg.s_content = summarized_content

            self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)
            self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)

    def sync_resume_to_qdrant(self, msg):
        payload = dict(json.loads(msg.value()))
        resume_id = dict(payload.get('after', {})).get('id')

        resume_agg = self.agg_repo.get_resume(resume_id)

        # Summarize job description
        summarized_content = self.ai_helper.get_resume_summarized(resume_agg.content)
        
        # Embed summarized job description
        vector = self.ai_helper.get_embedding(summarized_content)

        resume_agg.s_content = summarized_content

        self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_agg, vector)

    def sync_jobs_applied_resume_to_qdrant(self, msg):
        msg_dict = dict(json.loads(msg.value()))

        resume_id = dict(msg_dict.get('after', {})).get('id')

        jobs_id_list = self.agg_repo.get_list_job_id(resume_id)
        
        payload={
            "applied_jobs": jobs_id_list,
        },

        self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_id, payload)