from sqlalchemy.orm import Session

from app.dto import recruiter

from models.ccp_address import Address
from models.ccp_candidate import Candidate
from models.ccp_city import City
from models.ccp_country import Country
from models.ccp_job import Job
from models.ccp_talent_saved import TalentSaved
from models.ccp_user import User


class RecruiterRepository:      
    async def get_by_id(self, db:Session, id) -> User:
        result = db.query().filter(User.id == id).first()
        return result

    async def get_jobs_posted(self, db:Session, id) -> recruiter.ListJobsPostedResponse:
        result =  db.query(Job.id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
                                Job.salary_from, Job.salary_to, Job.job_type, Job.work_place,
                                 Job.company_type, Job.hiring_level, Job.created_at, Job.updated_at, Job.applied_count, Job.display_content).filter(Job.recruiter_id == id).all()
        record = []
        for job in result:
            record.append(
                recruiter.JobPostedResponse(
                    job_id=job.id,
                    job_title=job.job_title,
                    content=job.content,
                    is_hiring=job.is_hiring,
                    opened_date=job.opened_date,
                    closed_date=job.closed_date,
                    salary_from=job.salary_from,
                    salary_to=job.salary_to,
                    job_type=job.job_type,
                    work_place=job.work_place,
                    company_type=job.company_type,
                    hiring_level=job.hiring_level,
                    created_at=job.created_at,
                    updated_at=job.updated_at,
                    applied_count=job.applied_count,
                    display_content=job.display_content
                )
            )
        
        return recruiter.ListJobsPostedResponse (records=record)

    
    async def get_talents_saved(self, db:Session, id) -> recruiter.ListCandidateResponse:
        result = db.query(TalentSaved.candidate_id).filter(TalentSaved.recruiter_id == id).all()
        record = []
        for item in result:
            record.append(item.candidate_id)
        
        return recruiter.ListCandidateResponse(ids=record)
    