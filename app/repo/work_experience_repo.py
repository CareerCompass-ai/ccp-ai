from typing import List

from sqlalchemy.orm import Session

from models.ccp_work_experiences import WorkExperience


class WorkExperienceRepository:        
    async def list_by_candidate_id(self, db:Session, candidate_id) -> List[WorkExperience]:
        data = db.query(WorkExperience).filter(WorkExperience.candidate_id == candidate_id).all()
        return data
    