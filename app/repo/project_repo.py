from typing import List

from sqlalchemy.orm import Session

from models.ccp_project import Project


class ProjectRepository:        
    async def list_by_candidate_id(self, db:Session, candidate_id) -> List[Project]:
        data = db.query(Project).filter(Project.candidate_id == candidate_id).all()
        return data
    