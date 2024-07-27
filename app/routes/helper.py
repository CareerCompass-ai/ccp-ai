from app.dto import job
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd

import markdownify
import markdown2
from weasyprint import HTML

# Function to convert HTML to Markdown
async def html_to_markdown(self, html_content):
    return markdownify.markdownify(html_content, heading_style="ATX")

# Function to convert Markdown to PDF
async def markdown_to_pdf(self, markdown_content, output_path):
    html_content = markdown2.markdown(markdown_content)
    HTML(string=html_content).write_pdf(output_path)


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

async def generate_analysis_file(db: Session, time_from: str, time_to: str, file_name_job: str, file_name_user: str):
    query1 = f"""
        SELECT
            j.id AS "job_id (ID of the job)",
            j.job_title AS "job_title (Title of the job)",
            j.common_job_title AS "common_job_title (Common title of the job)",
            j.is_hiring AS "is_hiring (Job is opened or closed)",
            j.salary_from AS "salary_from (Minimum salary)",
            j.salary_to AS "salary_to (Maximum salary)",
            (j.salary_from + j.salary_to) / 2 AS "average_salary (Average salary)",
            j.job_type AS "job_type (Type of job)",
            j.company_type AS "company_type (Type of company)",
            j.work_place AS "work_place (Place of work)",
            j.applied_count AS "applied_count (Number of job applications)",
            j.hiring_level AS "hiring_level (Level of hiring)",
            j.created_at AS "created_at (Job creation date)",
            j.opened_date AS "opened_date (Job opened date)",
            j.closed_date AS "closed_date (Job closed date)",
            c.city_name AS "city_name (Name of the city)",
            co.country_name AS "country_name (Name of the country)",
            j.recruiter_id AS "recruiter_id (ID of the recruiter)",
            u.email AS "email (email of the recruiter)",
            u.phone AS "phone (phone of the recruiter)",
            COALESCE((
                SELECT STRING_AGG(t.tag_name, ', ')
                FROM ccp_jobtags jt
                JOIN ccp_tag t ON jt.tag_id = t.id
                WHERE jt.job_id = j.id
            ), '') AS "job_tags (Skills of the job)",
            COALESCE((
                SELECT COUNT(*)
                FROM ccp_recently_viewed_job rvj
                WHERE rvj.job_id = j.id
            ), 0) AS "total_view_count (Total View Count)"
        FROM ccp_job j
        JOIN ccp_address a ON j.address_id = a.id
        JOIN ccp_city c ON a.city_id = c.id
        JOIN ccp_country co ON c.country_id = co.id
        JOIN ccp_user u ON j.recruiter_id = u.id
        WHERE j.opened_date BETWEEN '{time_from}' AND '{time_to}'
        ORDER BY j.id ASC;
    """
    res_1 = db.execute(text(query1))
    columns = [
        "job_id (ID of the job)", 
        "job_title (Title of the job)",
        "common_job_title (Common title of the job)",
        "is_hiring (Job is opened or closed)",
        "salary_from (Minimum salary)", 
        "salary_to (Maximum salary)",
        "average_salary (Average salary)", 
        "job_type (Type of job)", 
        "company_type (Type of company)", 
        "work_place (Place of work)", 
        "applied_count (Number of job applications)",
        "hiring_level (Level of hiring)", 
        "created_at (Job creation date)",
        "opened_date (Job opened date)",
        "closed_date (Job closed date)",
        "city_name (Name of the city)", 
        "country_name (Name of the country)", 
        "recruiter_id (ID of the recruiter)",
        "email (email of the recruiter)",
        "phone (phone of the recruiter)",
        "job_tags (Skills of the job)",
        "total_view_count (Total View Count)"
    ]

    df1 = pd.DataFrame(res_1, columns=columns)
    with open(file_name_job, 'w', newline='') as f:
        df1.to_csv(f, index=False)
    f.close()

    query4 = f"""
        SELECT 
            u.id AS "user_id (ID of the user)", 
            c.city_name AS "city_name (Name of the city)", 
            co.country_name AS "country_name (Name of the country)", 
            u.role AS "role (Role of the user)", 
            u.work_title AS "candidate_work_title (Title of the work)", 
            ca.year_of_experience AS "candidate_yoe (Years of experience)", 
            ca.level AS "candidate_level (Level of the candidate)",
            u.created_at AS "created_at (Account creation date)"
        FROM ccp_user u 
        LEFT JOIN ccp_address a ON u.address_id = a.id
        LEFT JOIN ccp_city c ON a.city_id = c.id
        LEFT JOIN ccp_country co ON c.country_id = co.id
        LEFT JOIN ccp_candidate ca ON u.id = ca.id;
        --WHERE u.created_at BETWEEN '{time_from}' AND '{time_to}';
    """

    res_4 = db.execute(text(query4))

    columns = [
        "user_id (ID of the user)", 
        "city_name (Name of the city)", 
        "country_name (Name of the country)", 
        "role (Role of the user)", 
        "candidate_work_title (Title of the work)", 
        "candidate_yoe (Years of experience)", 
        "candidate_level (Level of the candidate)",
        "created_at (Account creation date)"
    ]

    df4 = pd.DataFrame(res_4, columns=columns)

    with open(file_name_user, 'a', newline='') as f:
        df4.to_csv(f, index=False)
    f.close()