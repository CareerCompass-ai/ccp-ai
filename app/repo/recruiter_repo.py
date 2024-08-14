from sqlalchemy.orm import Session

from app.dto import recruiter

from models.ccp_address import Address
from models.ccp_candidate import Candidate
from models.ccp_city import City
from models.ccp_country import Country
from models.ccp_job import Job
from models.ccp_talent_saved import TalentSaved
from models.ccp_user import User
from typing import List

class RecruiterRepository:      
    async def get_by_id(self, db:Session, id) -> User:
        result = db.query().filter(User.id == id).first()
        return result

    async def get_jobs_posted(self, db: Session, id: int, is_hiring: bool, input: str, offset: int, limit: int):
        query = db.query(Job.id).filter(
            Job.recruiter_id == id,
            Job.is_hiring == is_hiring,
            Job.status == 1
        )
        
        if input:
            query = query.filter(Job.job_title.ilike(f"%{input}%"))
        
        total_records = query.count()
        
        result = query.order_by(Job.updated_at.desc()).offset(offset).limit(limit).all()
        
        records = [job.id for job in result]
        
        return total_records, records

    
    async def get_talents_saved(self, db:Session, id) -> List[int]:
        result = db.query(TalentSaved.resume_id)\
                            .filter(TalentSaved.recruiter_id == id)\
                            .order_by(TalentSaved.created_at.desc())\
                            .all()
        record = []
        for item in result:
            record.append(item.resume_id)
        return record
    