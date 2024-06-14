from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.dto.job import JobAggregate
from app.dto.resume import ResumeAggregate
from app.repo.address_repo import AddressRepository
from app.repo.application_repo import ApplicationRepository
from app.repo.candidate_repo import CandidateRepository
from app.repo.candidate_skills_repo import CandidateSkillsRepository
from app.repo.city_repo import CityRepository
from app.repo.country_repo import CountryRepository
from app.repo.job_repo import JobRepository
from app.repo.jobtags_repo import JobTagsRepository
from app.repo.resume_repo import ResumeRepository
from app.repo.tag_repo import TagRepository
from app.repo.user_repo import UserRepository


class Aggregate:
    def __init__(self):
        self.job_repo = JobRepository()
        self.resume_repo = ResumeRepository()
        self.country_repo = CountryRepository()
        self.city_repo = CityRepository()
        self.address_repo = AddressRepository()
        self.tag_repo = TagRepository()
        self.jobtags_repo = JobTagsRepository()
        self.user_repo = UserRepository()
        self.candidate_repo = CandidateRepository()
        self.application_repo = ApplicationRepository()
        self.candidate_skills_repo = CandidateSkillsRepository()

    async def get_job(self, db:Session, id: int) -> Optional[JobAggregate]:
        job = await self.job_repo.get_by_id(db=db, id=id)

        if job is None:
            raise ValueError(f"Job with ID {id} not found")
        
        job_aggregate = JobAggregate(
            id=job.id,
            applied_count=job.applied_count,
            hiring_level=job.hiring_level,
            job_title=job.job_title,
            content=job.content,
            content_url=job.content_url,
            is_hiring=job.is_hiring,
            salary_from=job.salary_from,
            salary_to=job.salary_to,
            job_type=job.job_type,
            company_type=job.company_type,
            work_place=job.work_place
        )

        if job.updated_at is not None:
            job_aggregate.updated_at = datetime.fromisoformat(str(job.updated_at))

        if job.created_at is not None:
            job_aggregate.created_at = datetime.fromisoformat(str(job.created_at))

        if job.opened_date is not None:
            job_aggregate.opened_date = datetime.fromisoformat(str(job.opened_date))

        if job.closed_date is not None:
            job_aggregate.closed_date = datetime.fromisoformat(str(job.closed_date))
            
        if job.recruiter_id is not None:
            job_aggregate.recruiter_id = job.recruiter_id
            user = await self.user_repo.get_by_id(db=db, id=job.recruiter_id)
            if user is not None:
                job_aggregate.recruiter_name = user.first_name + ' ' + user.last_name

        if job.address_id is not None:
            address = await self.address_repo.get_by_id(db=db, id=job.address_id)
            job_aggregate.address_id = job.address_id
            
            #detailed_address is optional, city and country always exist
            city = await self.city_repo.get_by_id(db=db, id=address.city_id)

            country = await self.country_repo.get_by_id(db=db, id=city.country_id)

            address_full = ""
            if address.detailed_address is not None:
                address_full = f"{address.detailed_address}, {city.city_name}, {country.country_name}"
            else:
                address_full = f"{city.city_name}, {country.country_name}"

            job_aggregate.address = address_full
            job_aggregate.city_name = city.city_name
            job_aggregate.country_name = country.country_name

        job_tag_list = await self.jobtags_repo.get_jobtags_for_job(db=db, job_id=job_aggregate.id)
        
        tag_list = []
        for job_tag in job_tag_list:
            tag = await self.tag_repo.get_by_id(db=db, id=job_tag.tag_id)
            if tag:
                tag_list.append(tag.tag_name)
        
        job_aggregate.job_tags = tag_list
        
        return job_aggregate

    
    async def get_resume(self, db:Session, id: int) -> Optional[ResumeAggregate]:
        resume = await self.resume_repo.get_by_id(db=db, id=id)

        if resume is None:
            raise ValueError(f"Resume with ID {id} not found")

        resume_aggregate = ResumeAggregate(
            id = resume.id,
            content=resume.content,
            resume_link=resume.resume_link,
            resume_name=resume.resume_name
        )

        if resume.created_at is not None:
            resume_aggregate.created_at = datetime.fromisoformat(str(resume.created_at))

        if resume.updated_at is not None:
            resume_aggregate.updated_at = datetime.fromisoformat(str(resume.updated_at))
        
        if resume.candidate_id is not None:
            resume_aggregate.candidate_id = resume.candidate_id
            user = await self.user_repo.get_by_id(db=db, id=resume.candidate_id)
            if user is not None:
                resume_aggregate.candidate_name = user.first_name + ' ' + user.last_name
                resume_aggregate.work_title = user.work_title
                address = await self.address_repo.get_by_id(db=db, id=user.address_id)
                if address is not None:
                    city = await self.city_repo.get_by_id(db=db, id=address.city_id)
                    country = await self.country_repo.get_by_id(db=db, id=city.country_id)
                    resume_aggregate.candidate_address = address.detailed_address + ', ' + city.city_name + ', ' + country.country_name
            
            candidate = await self.candidate_repo.get_by_id(db=db, id=resume.candidate_id)
            if candidate is not None:
                resume_aggregate.open_to_work = candidate.open_to_work
                resume_aggregate.level = candidate.level
            
            candidate_skills_list = await self.candidate_skills_repo.get_by_id(db=db, id=resume.candidate_id)
            skill_list = []
            for i in candidate_skills_list:
                skill = await self.tag_repo.get_by_id(db=db, id=i.skill_id)
                skill_list.append(skill.tag_name)
            resume_aggregate.skills = skill_list
            
        return resume_aggregate

    async def get_list_job_id(self, db:Session, id: int):
        job_id_list = await self.application_repo.get_job_ids_by_resume_id(db=db, resume_id=id)
        return job_id_list
