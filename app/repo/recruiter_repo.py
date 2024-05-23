from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_job import Job
from models.ccp_talent_saved import TalentSaved
from models.ccp_address import Address
from models.ccp_candidate import Candidate
from models.ccp_user import User
from models.ccp_city import City
from models.ccp_country import Country

from app.dto import recruiter

class RecruiterRepository:        
    async def get_jobs_posted(self, db:Session, id) -> recruiter.ListJobsPostedResponse:
        result =  db.query(Job.id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
                                Job.salary_from, Job.salary_to, Job.job_type, Job.work_place,
                                 Job.company_type, Job.hiring_level, Job.created_at, Job.updated_at, Job.applied_count).filter(Job.recruiter_id == id).all()
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
                    applied_count=job.applied_count
                )
            )
        
        return recruiter.ListJobsPostedResponse (records=record)

    
    async def get_talents_saved(self, db:Session, id) -> recruiter.ListTalentSavedResponse:
        result = db.query(TalentSaved.candidate_id, Candidate.year_of_experience, Candidate.open_to_work, Candidate.self_introduction, Candidate.level,
                               User.email, User.phone, User.first_name, User.last_name, User.work_title, User.gender, User.dob,
                               Address.detailed_address, City.city_name, Country.country_name) \
                            .join(Candidate, TalentSaved.candidate_id == Candidate.id)\
                            .join(User, Candidate.id == User.id)\
                            .join(Address, User.address_id == Address.id)\
                            .join(City, Address.city_id == City.id)\
                            .join(Country, City.country_id == Country.id)\
                            .filter(TalentSaved.recruiter_id == id)\
                            .all()
        record = []
        for item in result:
            record.append(
                recruiter.TalentSavedResponse(
                    candidate_id=item.candidate_id,
                    year_of_experience=item.year_of_experience,
                    open_to_work=item.open_to_work,
                    self_introduction=item.self_introduction,
                    level=item.level,
                    email=item.email,
                    phone=item.phone,
                    first_name=item.first_name,
                    last_name=item.last_name,
                    work_title=item.work_title,
                    gender=item.gender,
                    dob=item.dob,
                    detailed_address=item.detailed_address,
                    city_name=item.city_name,
                    country_name=item.country_name
                )
            )
        
        return recruiter.ListTalentSavedResponse(records=record)
    