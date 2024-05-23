from config.postgres import SessionLocal
from models.ccp_talent_saved import TalentSaved

class TalentSavedRepository:
    def __init__(self):
        self.db = SessionLocal() 


    async def create_saved_talent(self, record: TalentSaved) -> TalentSaved:
        self.db.add(record)
        self.db.commit()
        
        return record
    
    async def delete_saved_talent(self, record: TalentSaved) -> TalentSaved:
        self.db.query(TalentSaved).filter_by(candidate_id = record.candidate_id, recruiter_id = record.recruiter_id).delete()
        self.db.commit()

        return record