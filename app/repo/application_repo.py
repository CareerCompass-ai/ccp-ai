from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_application import Application



class ApplicationRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_ids(self, resume_id, job_id):
        return self.db.query(Application).filter(Application.resume_id == resume_id and Application.job_id == job_id).first()