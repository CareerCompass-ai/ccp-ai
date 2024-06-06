import hashlib
import json

from fastapi import Depends
from sqlalchemy.orm import Session

import constant.config as constant
from app.ai.ai_helper import AI
from app.dto import application
from app.repo.aggregate import Aggregate
from config.postgres import PostgresDB
from config.qdrant import QdrantVDB
from config.weaviate import WeaviateVDB

from .sync_helper import SyncHelper

# from elasticsearch import Elasticsearch




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

    async def sync_job_to_qdrant_and_weaviate(self, msg, db: Session = Depends(PostgresDB.get_db)):
        payload = dict(json.loads(msg.value()))
        job_id = dict(payload.get('after', {})).get('id')

        job_agg = await self.agg_repo.get_job(db=db, id=job_id)

        if 'before' in payload and payload['before'] is not None:
            old_content = str(payload['before']['content'])
            new_content = str(payload['after']['content'])

            # save money
            if hashlib.md5(old_content.encode()).hexdigest() != hashlib.md5(new_content.encode()).hexdigest():
                summarized_content = await self.ai_helper.get_job_summarized(job_agg.content)
                vector = await self.ai_helper.get_embedding(summarized_content)
                job_agg.s_content = summarized_content

                await self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)
                # TODO: handle update object in weaviate
                # self.sync_helper.insert_to_weaviate("Job", job_agg)
                # self.sync_helper.insert_to_weaviate("JobQnA", job_agg)
                # self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)
                await self.sync_helper.replace_object_weaviate("Job", job_agg)
            else:
                # TODO: Handle update object fields in weaviate 
                # NOTE: weaviate uses uuid. We have already included `job_id` in the payload synced to weaviate, so we might get by job_id then update by the job.uuid
                if hasattr(job_agg, "s_content"):
                    delattr(job_agg, "s_content")
                await self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_id, job_agg.model_dump())
                await self.sync_helper.replace_object_weaviate("Job", job_agg)
                # self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)
        else:
            summarized_content = await self.ai_helper.get_job_summarized(job_agg.content)
            vector = await self.ai_helper.get_embedding(summarized_content)
            job_agg.s_content = summarized_content

            await self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_JOB_SEARCH, job_agg, vector)
            await self.sync_helper.insert_to_weaviate("JobQnA", job_agg)
            await self.sync_helper.insert_to_weaviate("Job", job_agg)
            # self.sync_helper.upsert_to_es(constant.ES_INDEX_JOB_SEARCH, job_agg)

    async def sync_resume_to_qdrant(self, msg, db: Session = Depends(PostgresDB.get_db)):
        payload = dict(json.loads(msg.value()))
        resume_id = dict(payload.get('after', {})).get('id')

        resume_agg = await self.agg_repo.get_resume(db=db, id=resume_id)

        if 'before' in payload and payload['before'] is not None:
            await self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_id, resume_agg.model_dump())
        else:
            summarized_content = await self.ai_helper.get_resume_summarized(resume_agg.content)
            vector = await self.ai_helper.get_embedding(summarized_content)
            resume_agg.s_content = summarized_content

            await self.sync_helper.upsert_to_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_agg, vector)
            

    async def sync_jobs_applied_resume_to_qdrant(self, msg, db: Session = Depends(PostgresDB.get_db)):
        msg_dict = dict(json.loads(msg.value()))

        resume_id = dict(msg_dict.get('after', {})).get('resume_id')

        jobs_id_list = await self.agg_repo.get_list_job_id(db=db, id=resume_id)
        
        payload = application.ListJobResponse(
            applied_jobs=jobs_id_list
        )

        record = payload.model_dump()
        await self.sync_helper.update_fields_qdrant(constant.QDRANT_INDEX_RESUME_SEARCH, resume_id, record)
        await self.sync_helper.update_object_properties_weaviate("Resume", record)
        # TODO: Handle update object fields in weaviate 