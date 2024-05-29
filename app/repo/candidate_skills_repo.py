from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_candidate_skills import Candidate_Skills

class CandidateSkillsRepository:
    async def get_by_id(self, db:Session, id):
        return db.query(Candidate_Skills).filter(Candidate_Skills.candidate_id == id).all()
    
    # def get_jobtags(self, db: Session) -> List[JobTag]:
    #     tags = db.query(JobTag).all()
    #     jobtag_aggregates = []
    #     for item in tags:
    #         jobtag_aggregate = job_tag.JobTagsBase(
    #             tag_id=item.tag_id,
    #             job_id=item.job_id, 
    #             created_at= item.created_at,
    #             updated_at=item.updated_at
    #         )
    #         jobtag_aggregates.append(jobtag_aggregate)
    #     return jobtag_aggregates
    
    # def get_jobtags_for_job(self, job_id: int) -> List[JobTag]:
    #     tags = self.db.query(JobTag).filter(JobTag.job_id == job_id).all()
    #     jobtag_aggregates = []
    #     for item in tags:
    #         jobtag_aggregate = job_tag.JobTagsBase(
    #             tag_id=item.tag_id,
    #             job_id=item.job_id, 
    #             created_at= item.created_at,
    #             updated_at=item.updated_at
    #         )
    #         jobtag_aggregates.append(jobtag_aggregate)
    #     return jobtag_aggregates
