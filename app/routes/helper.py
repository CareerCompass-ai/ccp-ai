from app.dto import job

async def combine_job_content(job_agg: job.JobAggregate, summarized_content: str, acronyms_and_abbreviations: str) -> str:
        combined_content = (
            summarized_content + " " +
            job_agg.job_title + " " + 
            job_agg.job_type + " " + 
            job_agg.company_type + " " +
            job_agg.work_place + " " +
            job_agg.address + " " +
            job_agg.city_name + " " +
            job_agg.country_name + " " +
            job_agg.hiring_level + " " +
            job_agg.common_job_title + " " + 
            acronyms_and_abbreviations
        )
        return combined_content