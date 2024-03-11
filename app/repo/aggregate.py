from typing import List, Optional

from app.repo.job_repo import JobRepository

from app.dto.job import JobAggregate 

class Aggregate:
    def __init__(self):
        self.job_repo = JobRepository()

    def get_job(self, id: int) -> Optional[JobAggregate]:
        job = self.job_repo.get_by_id(id)

        if job is None:
            raise ValueError(f"Job with ID {id} not found")
        
        # TODO: Aggregating data ...
        # user_id = self.get_user_id_for_job(id) # example
        job_aggregate = JobAggregate(
            id=job.id,
            title=job.title,
            content=job.content,
            # user_id=user_id,  # example
            # Add more fields
        )

        return job_aggregate


