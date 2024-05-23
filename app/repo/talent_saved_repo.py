from config.postgres import SessionLocal
from models.ccp_talent_saved import TalentSaved
from sqlalchemy.orm import Session
class TalentSavedRepository:
    async def create_saved_talent(self, db:Session, record: TalentSaved) -> TalentSaved:
        db.add(record)
        db.commit()
        
        return record
    
    async def delete_saved_talent(self, db:Session, record: TalentSaved) -> TalentSaved:
        db.query(TalentSaved).filter_by(candidate_id = record.candidate_id, recruiter_id = record.recruiter_id).delete()
        db.commit()

        return record