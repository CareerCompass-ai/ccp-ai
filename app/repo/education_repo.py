from typing import List

from sqlalchemy.orm import Session

from models.ccp_education import Education


class EducationRepository:        
    async def list_by_candidate_id(self, db:Session, candidate_id) -> List[Education]:
        data = db.query(Education).filter(Education.candidate_id == candidate_id).all()
        return data
    