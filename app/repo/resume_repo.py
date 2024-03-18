from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models import ccp_resume
from models.ccp_resume import Resume
from models.ccp_candidate import Candidate
from models.ccp_user import User
class ResumeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_resume(self, id):
        result = self.db.query(Resume).filter(Resume.id == id).first()
        return result
    def get_candidate(self, id):
        return self.db.query(Candidate).filter(Candidate.id == id).first()
    def get_user(self, id):
        return self.db.query(User).filter(User.id == id).first()