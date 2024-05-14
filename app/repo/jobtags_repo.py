from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_jobtag import JobTag
from app.dto import job_tag

from typing import List


class JobTagsRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def get_by_id(self, id_tag, id_job):
        return self.db.query(JobTag).filter(JobTag.tag_id == id_tag and JobTag.job_id == id_job).first()
    
    def get_jobtags(self, db: Session) -> List[JobTag]:
        tags = db.query(JobTag).all()
        jobtag_aggregates = []
        for item in tags:
            jobtag_aggregate = job_tag.JobTagsBase(
                tag_id=item.tag_id,
                job_id=item.job_id, 
                created_at= item.created_at,
                updated_at=item.updated_at
            )
            jobtag_aggregates.append(jobtag_aggregate)

        self.db.close()
        
        return jobtag_aggregates
    
    def get_jobtags_for_job(self, job_id: int) -> List[JobTag]:
        tags = self.db.query(JobTag).filter(JobTag.job_id == job_id).all()
        jobtag_aggregates = []
        for item in tags:
            jobtag_aggregate = job_tag.JobTagsBase(
                tag_id=item.tag_id,
                job_id=item.job_id, 
                created_at= item.created_at,
                updated_at=item.updated_at
            )
            jobtag_aggregates.append(jobtag_aggregate)

        self.db.close()

        return jobtag_aggregates
    
    def create(self, session: Session, tag_id: int, job_id: int) -> JobTag:
        record = JobTag(tag_id=tag_id, job_id=job_id)
        session.add(record)
        session.flush()  
        session.refresh(record)  

        return record

    def delete_jobtags(self, job_id: int):
        self.db.query(JobTag).filter(JobTag.job_id == job_id).delete()
        self.db.commit()