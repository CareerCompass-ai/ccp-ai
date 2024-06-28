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

    async def get_jobs_posted(self, db:Session, id) -> List[int]:
        result = db.query(
            Job.id
        ).filter(
            Job.recruiter_id == id
        ).order_by(Job.created_at.desc()
        ).all()
        records = []
        for job in result:
            records.append(job.id)
        
        return records

    
    async def get_talents_saved(self, db:Session, id) -> List[int]:
        result = db.query(TalentSaved.resume_id)\
                            .filter(TalentSaved.recruiter_id == id)\
                            .order_by(TalentSaved.created_at.desc())\
                            .all()
        record = []
        for item in result:
            record.append(item.resume_id)
        return record
    