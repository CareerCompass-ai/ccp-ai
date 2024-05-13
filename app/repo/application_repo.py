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
    
    async def create(self, session: Session, record: Application) -> Application:
        session.add(record)
        session.flush()
        session.refresh(record)

        return record
    
    async def list_by_resume_ids(self, db:Session, resume_ids: list[int], job_id: int) -> list[Application]:
        applications = (
            self.db.query(Application).
            filter(Application.resume_id.in_(resume_ids), Application.job_id == job_id).
            all()
        )

        db.close()
        return applications
