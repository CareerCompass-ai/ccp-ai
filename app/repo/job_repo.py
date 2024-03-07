from ...config.database import SessionLocal
from ...models.ccp_job import Job

class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, job_id):
        return self.db.query(Job).filter(Job.id == job_id).first()
