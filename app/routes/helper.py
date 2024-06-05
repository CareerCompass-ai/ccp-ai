from app.dto import job
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import pandas as pd


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

async def generate_analysis_file(db: Session, time_from: str, time_to: str, file_name: str):
    query1 = f"""
    SELECT
        j.id AS "job_id (ID of the job)",
        j.job_title AS "job_title (Title of the job)",
        j.common_job_title AS "common_job_title (Common title of the job)",
        j.salary_from AS "salary_from (Minimum salary)",
        j.salary_to AS "salary_to (Maximum salary)",
        (j.salary_from + j.salary_to) / 2 AS "average_salary (Average salary)",
        j.job_type AS "job_type (Type of job)",
        j.company_type AS "company_type (Type of company)",
        j.work_place AS "work_place (Place of work)",
        j.applied_count AS "applied_count (Number of job applications)",
        j.hiring_level AS "hiring_level (Level of hiring)",
        c.city_name AS "city_name (Name of the city)",
        co.country_name AS "country_name (Name of the country)",
        j.recruiter_id AS "recruiter_id (ID of the recruiter)"
    FROM ccp_job j
    JOIN ccp_address a ON j.address_id = a.id
    JOIN ccp_city c ON a.city_id = c.id
    JOIN ccp_country co ON c.country_id = co.id
    WHERE j.updated_at BETWEEN '{time_from}' AND '{time_to}'
    ORDER BY j.id ASC;
    """
    res_1 = db.execute(text(query1))
    columns = [
        "job_id (ID of the job)", 
        "job_title (Title of the job)",
        "common_job_title (Common title of the job)",
        "salary_from (Minimum salary)", 
        "salary_to (Maximum salary)",
        "average_salary (Average salary)", 
        "job_type (Type of job)", 
        "company_type (Type of company)", 
        "work_place (Place of work)", 
        "applied_count (Number of job applications)",
        "hiring_level (Level of hiring)", 
        "city_name (Name of the city)", 
        "country_name (Name of the country)", 
        "recruiter_id (ID of the recruiter)"
    ]

    df1 = pd.DataFrame(res_1, columns=columns)
    with open(file_name, 'w', newline='') as f:
        f.write('Description: Job details with associated location and recruiter information.\n')
        df1.to_csv(f, index=False)
        f.write('\n')

    query2 = f"""
        SELECT jt.job_id AS "job_id", t.tag_name AS "skill_name (Name of the skill)"
        FROM ccp_jobtags jt
        JOIN ccp_tag t ON jt.tag_id = t.id;
       --WHERE jt.updated_at BETWEEN '{time_from}' AND '{time_to}';
    """
    res_2 = db.execute(text(query2))
    columns = ["job_id", "skill_name (Name of the skill)"]
    df2 = pd.DataFrame(res_2, columns=columns)

    df_grouped = df2.groupby('job_id')['skill_name (Name of the skill)'].apply(lambda x: ','.join(x)).reset_index()

    with open(file_name, 'a', newline='') as f:
        f.write('Description: Job skills grouped by job ID.\n')
        df_grouped.to_csv(f, index=False)
        f.write('\n')

    query3 = f"""
        SELECT job_id, COUNT(id) AS "view_count (Number of views)"
        FROM ccp_recently_viewed_job
        WHERE created_at BETWEEN '{time_from}' AND '{time_to}'
        GROUP BY job_id
        ORDER BY COUNT(id) DESC;
    """
    res_3 = db.execute(text(query3))

    columns = ["job_id", "view_count (Number of views)"]
    df3 = pd.DataFrame(res_3, columns=columns)

    with open(file_name, 'a', newline='') as f:
        f.write('Description: Recently viewed job counts grouped by job ID.\n')
        df3.to_csv(f, index=False)
        f.write('\n')

    query4 = f"""
        SELECT 
            u.id AS "user_id (ID of the user)", 
            c.city_name AS "city_name (Name of the city)", 
            co.country_name AS "country_name (Name of the country)", 
            u.role AS "role (Role of the user)", 
            u.work_title AS "candidate_work_title (Title of the work)", 
            ca.year_of_experience AS "candidate_yoe (Years of experience)", 
            ca.level AS "candidate_level (Level of the candidate)"
        FROM ccp_user u 
        JOIN ccp_address a ON u.address_id = a.id
        JOIN ccp_city c ON a.city_id = c.id
        JOIN ccp_country co ON c.country_id = co.id
        LEFT JOIN ccp_candidate ca ON u.id = ca.id;
        --WHERE u.created_at BETWEEN '{time_from}' AND '{time_to}'
    """

    res_4 = db.execute(text(query4))

    columns = [
        "user_id (ID of the user)", 
        "city_name (Name of the city)", 
        "country_name (Name of the country)", 
        "role (Role of the user)", 
        "candidate_work_title (Title of the work)", 
        "candidate_yoe (Years of experience)", 
        "candidate_level (Level of the candidate)"
    ]

    df4 = pd.DataFrame(res_4, columns=columns)

    with open(file_name, 'a', newline='') as f:
        f.write('Description: User details with associated location and candidate experience.\n')
        df4.to_csv(f, index=False)
        f.write('\n')

    f.close()