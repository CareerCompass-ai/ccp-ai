from app.repo.job_repo import JobRepository

from app.dto.job import JobAggregate 

from app.dto import job as job

class Aggregate:
    def __init__(self):
        self.job_repo = JobRepository()

    def get_job(self, id):
        job = self.job_repo.get_by_id(id=id)

        if job is None:
            raise ValueError(f"Job with ID {id} not found")
        
        # TODO: Aggregating data ...
        # user_id = self.get_user_id_for_job(id) # example


