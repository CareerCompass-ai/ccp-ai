from typing import List, Optional

from app.dto.job import JobAggregate 

from app.repo.job_repo import JobRepository
from app.repo.resume_repo import ResumeRepository
from app.repo.country_repo import CountryRepository
from app.repo.city_repo import CityRepository
from app.repo.address_repo import AddressRepository
from app.repo.jobtags_repo import JobTagsRepository
from app.repo.tag_repo import TagRepository
from app.dto.resume import ResumeAggregate

class Aggregate:
    def __init__(self):
        self.job_repo = JobRepository()
        self.resume_repo = ResumeRepository()
        self.country_repo = CountryRepository()
        self.city_repo = CityRepository()
        self.address_repo = AddressRepository()
        self.tag_repo = TagRepository()
        self.jobtags_repo = JobTagsRepository()

    def get_job(self, id: int) -> Optional[JobAggregate]:
        job = self.job_repo.get_by_id(id)

        if job is None:
            raise ValueError(f"Job with ID {id} not found")
        
        job_aggregate = JobAggregate(
            id=job.id,
            title=job.title,
            content=job.content,
            content_url = job.content_url,
            is_hiring = job.is_hiring,
            opened_date = job.opened_date,
            closed_date = job.closed_date,
            salary_from = job.salary_from,
            salary_to = job.salary_to,
            job_type = job.job_type,
            company_type = job.company_type,
            created_at = job.created_at,
            updated_at = job.updated_at
        )

        address = self.address_repo.get_by_id(job.address_id)
        city = self.city_repo.get_by_id(address.city_id)
        country = self.country_repo.get_by_id(city.country_id)
        address_full = address.detailed_address + ', ' + city.city_name + ', ' + country.country_name
        
        job_aggregate.address = address_full
        
        job_tag_list = self.jobtags_repo.get_jobtags_for_job(job_aggregate.id)
        
        tag_list = []
        for job_tag in job_tag_list:
            tag = self.tag_repo.get_by_id(job_tag.tag_id)
            tag_list.append(tag.tag_name)
        
        job_aggregate.job_tags = tag_list
        
        return job_aggregate
    
    def get_resume(self, resume_id):
        resume = self.resume_repo.get_resume(resume_id)

        if resume is None:
            raise ValueError(f"Resume with ID {id} not found")

        candidate = self.resume_repo.get_candidate(resume.candidate_id)
        user = self.resume_repo.get_user(candidate.user_id)
        print(resume.id, candidate.id, user.id)

        return resume

