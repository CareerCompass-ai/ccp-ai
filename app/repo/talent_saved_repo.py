from sqlalchemy.orm import Session

from models.ccp_talent_saved import TalentSaved


class TalentSavedRepository:
    async def create_saved_talent(self, db:Session, record: TalentSaved) -> TalentSaved:
        db.add(record)
        db.commit()
        
        return record
    
    async def delete_saved_talent(self, db:Session, record: TalentSaved) -> TalentSaved:
        db.query(TalentSaved).filter_by(candidate_id = record.candidate_id, recruiter_id = record.recruiter_id, resume_id = record.resume_id).delete()
        db.commit()

        return record
    
    async def check_saved_talent(self, db:Session, resume_id: int, recruiter_id: int) -> bool:
        is_saved = db.query(TalentSaved).filter(TalentSaved.recruiter_id == recruiter_id, TalentSaved.resume_id == resume_id).first()

        if is_saved is None:
            return False
        return True