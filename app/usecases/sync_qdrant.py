from ..repo.job_repo import JobRepository

class SyncUseCase:
    def __init__(self):
        self.job_repo = JobRepository()

    def sync_job_to_qdrant(self, job_id):
        job = self.job_repo.get_by_id(job_id)

        if job:
            self.sync_to_qdrant(job)
            return True
        else:
            return False

    def sync_to_qdrant(self, job):
        print(f"Syncing job {job.id} to Qdrant")
