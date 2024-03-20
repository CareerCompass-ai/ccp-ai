from app.dto import job

def toJobDTO(payload: dict) -> job.JobAggregate:
    return job.JobAggregate(
        id=payload["id"],
        job_title=payload["job_title"],
        content=payload["content"],
        s_content=payload["s_content"],
        content_url=payload["content_url"],
        is_hiring=payload["is_hiring"],
        opened_date=payload["opened_date"],
        closed_date=payload["closed_date"],
        salary_from=payload["salary_from"],
        salary_to=payload["salary_to"],
        job_type=payload["job_type"],
        company_type=payload["company_type"],
        created_at=payload["created_at"],
        updated_at=payload["updated_at"],
        recruiter_id=payload["recruiter_id"],  
        recruiter_name=payload["recruiter_name"],
        job_tags=payload["job_tags"],
        address=payload["address"],
        hiring_level=payload["hiring_level"],
        applied_count=payload["applied_count"],
        address_id=payload["address_id"],
    )