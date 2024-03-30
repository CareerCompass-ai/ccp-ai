from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_application import Application



class ApplicationRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_job_ids_by_resume_id(self, resume_id):
        job_ids = (
            self.db.query(Application.job_id)
            .filter(Application.resume_id == resume_id)
            .all()
        )
        
        return [job_id for (job_id,) in job_ids]