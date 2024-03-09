from app.repo.job_repo import JobRepository
from qdrant_client import QdrantClient

class SyncUseCase:
    def __init__(self):
        self.job_repo = JobRepository()
        self.qdrant_client = QdrantClient()

    def sync_job_to_qdrant(self, job_id):
        job = self.job_repo.get_by_id(job_id)
        if job is None:
            raise ValueError(f"Job with ID {job_id} not found")

        # Aggregate data for Qdrant insertion
        job_vector = [job.salary_from, job.salary_to]
        metadata = {"id": job.id}  

        self.qdrant_client.upsert()

        print(f"Synced job {job.id} to Qdrant")

