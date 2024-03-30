from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_candidate import Candidate



class CandidateRepository:
    def __init__(self):
        self.db = SessionLocal()
    def get_by_id(self, id):
        return self.db.query(Candidate).filter(Candidate.id == id).first()