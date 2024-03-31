from config.postgres import SessionLocal

from models.ccp_resume import Resume

class ResumeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        result = self.db.query(Resume).filter(Resume.id == id).first()
        return result