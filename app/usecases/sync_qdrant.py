import json
import hashlib

from qdrant_client import QdrantClient

import constant.config as constant
from config.qdrant import QdrantVDB
from config.weaviate import WeaviateVDB
# from elasticsearch import Elasticsearch

from app.repo.aggregate import Aggregate

from app.ai.ai_helper import AI
from .sync_helper import SyncHelper
from app.dto import application

class SyncUsecase:
    def __init__(self):
        self.qdrant_client = QdrantVDB.setup_qdrant_connection()
        self.weaviate_client = WeaviateVDB.setup_weaviate_connection()
        # self.es_client = Elasticsearch(
        #     constant.ES_URL, 
        #     basic_auth=[constant.ES_USERNAME, constant.ES_PASSWORD], 
        # )

        self.ai_helper = AI()
        self.sync_helper = SyncHelper(qdrant_client=self.qdrant_client, weaviate_client=self.weaviate_client)

        self.agg_repo = Aggregate()

    def sync_job_to_qdrant_and_weaviate(self, msg):
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
                # TODO: handle update object in weaviate
                # self.sync_helper.insert_to_weaviate("Job", job_agg)
                # self.sync_helper.insert_to_weaviate("JobQnA", job_agg)
                # self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)
            else:
                # TODO: Handle update object fields in weaviate 
                # NOTE: weaviate uses uuid. We have already included `job_id` in the payload synced to weaviate, so we might get by job_id then update by the job.uuid
                self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_id, job_agg.model_dump())
                # self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)
        else:
            summarized_content = self.ai_helper.get_job_summarized(job_agg.content)
            vector = self.ai_helper.get_embedding(summarized_content)
            job_agg.s_content = summarized_content

            self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)
            self.sync_helper.insert_to_weaviate("JobQnA", job_agg)
            self.sync_helper.insert_to_weaviate("Job", job_agg)
            # self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)

    def sync_resume_to_qdrant(self, msg):
        payload = dict(json.loads(msg.value()))
        resume_id = dict(payload.get('after', {})).get('id')

        resume_agg = self.agg_repo.get_resume(resume_id)

        if 'before' in payload and payload['before'] is not None:
            self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_id, resume_agg.model_dump())
        else:
            summarized_content = self.ai_helper.get_resume_summarized(resume_agg.content)
            vector = self.ai_helper.get_embedding(summarized_content)
            resume_agg.s_content = summarized_content

            self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_agg, vector)
            

    def sync_jobs_applied_resume_to_qdrant(self, msg):
        msg_dict = dict(json.loads(msg.value()))

        resume_id = dict(msg_dict.get('after', {})).get('resume_id')

        jobs_id_list = self.agg_repo.get_list_job_id(resume_id)
        
        payload = application.ListJobResponse(
            applied_jobs=jobs_id_list
        )
        record = payload.model_dump()
        self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_id, record)
        # TODO: Handle update object fields in weaviate 