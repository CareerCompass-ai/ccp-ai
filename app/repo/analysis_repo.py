from typing import List

from config.postgres import SessionLocal, thread_local_session
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, and_, text
from models.ccp_job import Job
from models.ccp_application import Application
from models.ccp_jobtag import JobTag
from app.dto import analysis
from models.ccp_tag import Tag
from models.ccp_user import User
from models.ccp_viewedjob import ViewedJob
from models.ccp_candidate import Candidate
from models.ccp_city import City
from models.ccp_country import Country
from models.ccp_address import Address

class AnalysisRepository:
    async def get_top_job_titles(self, db:Session, top_number, time_from=None, time_to=None) -> analysis.ListTopJobTitlesResponse:
        query = db.query(Job.common_job_title, func.count(Job.id).label('job_count')) \
                    .filter(and_( Job.updated_at >= time_from, Job.updated_at<= time_to )) 

        query = query.group_by(Job.common_job_title).order_by(func.count(Job.id).desc()).limit(top_number)

        records = query.all()

        data = []
        for item in records:
            data.append(
                analysis.TopJobTitlesResponse(
                    job_title=item.common_job_title,
                    count=item.job_count
                )
            )
        
        return analysis.ListTopJobTitlesResponse (data=data)
    
    async def get_top_leader_salaries(self, db:Session, country_name = 'Vietnam', time = None, time_from=None, time_to = None, limit=0, order=1) -> analysis.ListTopJobTitlesSalaryResponse:
        if "'" not in country_name:
            country_name = f"'{country_name}'"
        sql_query = f'''
                    SELECT 
            common_job_title,
            hiring_level,
            ROUND(AVG(
                CASE 
                    WHEN salary_from IS NULL AND salary_to IS NOT NULL THEN salary_to
                    WHEN salary_from IS NOT NULL AND salary_to IS NULL THEN salary_from
                    ELSE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0
                END
            )) AS average_salary
        FROM 
            ccp_job
        LEFT JOIN ccp_address ON address_id = ccp_address.id
        LEFT JOIN ccp_city ON ccp_address.city_id = ccp_city.id
        LEFT JOIN ccp_country ON ccp_city.country_id = ccp_country.id
        WHERE 
            common_job_title != 'Other position' and country_name = {country_name} 
            '''
        if time is not None and time.lower() != 'none':
            time = time.lower()
            if "'" in time:
                time = time.replace("'", "")
            sql_query += f'''
             and ccp_job.updated_at BETWEEN CURRENT_DATE - INTERVAL '1 {time}' AND CURRENT_DATE '''
        elif time_from and time_to and time_from.lower() != 'none' and time_to.lower() != 'none':
            if "'" in time_to or "'" in time_from:
                time_from = time_from.replace("'", "")
                time_to =  time_to.replace("'", "")
            sql_query += f'''
             AND 
             ccp_job.updated_at >= to_date('{time_from}', 'YYYY/MM') 
            AND ccp_job.updated_at < to_date('{time_to}', 'YYYY/MM') + interval '1 month'
            '''

        sql_query += '''
         GROUP BY 
            common_job_title, 
            hiring_level
        ORDER BY 
            ROUND(AVG(
                CASE 
                    WHEN salary_from IS NULL AND salary_to IS NOT NULL THEN salary_to
                    WHEN salary_from IS NOT NULL AND salary_to IS NULL THEN salary_from
                    ELSE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0
                END
            ))
                '''
        if order != 0:
            sql_query += " DESC"
        else:
            sql_query += " ASC"
        if limit and limit > 0:
            sql_query += f" LIMIT {limit};"
        else:
            sql_query += ";"

        # Execute the SQL query
        result =  db.execute(text(sql_query))

        # Fetch all the rows from the result
        rows = result.fetchall()
        data = []

        for row in rows:
            # Create an instance of analysis.GetTopJobTitlesSalaryResponse
            item = analysis.GetTopJobTitlesSalaryResponse(
                job_title=row[0],  
                hiring_level=row[1], 
                average_salary=row[2]  
            )
            # Append the created instance to the data list
            data.append(item)

        return analysis.ListTopJobTitlesSalaryResponse(data=data)
    
    async def get_most_applied_job_titles(self, db:Session, top_number, time_from=None, time_to=None)-> analysis.ListTopAppliedJobTitlesResponse:
        query = db.query(Job.common_job_title, func.count().label('job_count')) \
                    .join(Application, Job.id == Application.job_id)
        if time_from and time_from != 'None' and time_to and time_to != None:
            query = query.filter(and_( Application.updated_at >= time_from, Application.updated_at<= time_to )) 

        query = query.group_by(Job.common_job_title) \
                    .order_by(func.count().desc()).limit(top_number)

        results = query.all()

        data = []
        for item in results:
            data.append (
                analysis.GetTopAppliedJobTitlesResponse (
                    job_title=item.common_job_title,
                    count=item.job_count
                )
            )

        return analysis.ListTopAppliedJobTitlesResponse(data=data)
    
    async def get_top_skills (self, db:Session, top_number:int, time: str) -> analysis.GetTopSkillResponse:
        if time and "'" in time[0]:
            time = time.replace("'", "")
        sql_query = f'''
        SELECT ccp_tag.id, ccp_tag.tag_name, count(ccp_tag.id) as count
        FROM ccp_tag
        JOIN ccp_jobtags on ccp_tag.id = ccp_jobtags.tag_id
        WHERE 
            ccp_jobtags.updated_at BETWEEN CURRENT_DATE - INTERVAL '1 {time}' AND CURRENT_DATE
        GROUP BY ccp_tag.id, ccp_tag.tag_name
        ORDER BY count DESC
        LIMIT {top_number}
        '''
        records = db.execute(text(sql_query))
        data = []

        for item in records:
            data.append (
                analysis.TopSkillResponse(
                    id=item.id,
                    skill=item.tag_name,
                    count=item.count
                )
            )
        
        db.close()
        
        return analysis.GetTopSkillResponse(data=data) 

    # async def get_top_skills (self, db:Session, top_number:int) -> analysis.GetTopSkillResponse:
    #     records = db.query(Tag.id, Tag.tag_name, func.count(Tag.id).label('skill_count')) \
    #                     .join(JobTag, Tag.id == JobTag.tag_id) \
    #                     .group_by(Tag.id, Tag.tag_name) \
    #                     .order_by(desc('skill_count')) \
    #                     .limit(top_number) \
    #                     .all()
        
    #     data = []

    #     for item in records:
    #         data.append (
    #             analysis.TopSkillResponse(
    #                 id=item.id,
    #                 skill=item.tag_name,
    #                 count=item.count
    #             )
    #         )
        
    #     db.close()
        
    #     return analysis.GetTopSkillResponse(data=data)        
    
    async def number_of_company_type (self, db:Session) -> analysis.GetNumberOfCompanyTypeResponse:
        records = db.query(Job.company_type, func.count(Job.id).label('company_type_count')).group_by(Job.company_type).all()
        
        data = []
        for item in records:
            data.append(
                analysis.NumberOfCompanyTypeResponse(
                    company_type=item.company_type,
                    count = item.company_type_count
                )
            )    

        return analysis.GetNumberOfCompanyTypeResponse(data=data)
    
    async def get_number_of_new_user(self, db:Session, time_from, time_to) -> analysis.GetNumberOfNewUser:
        records = db.query(User.id, User.role, User.created_at) \
                        .filter(and_(User.created_at >= time_from,User.created_at <= time_to )) \
                        .all()
        
        data = []
        for item in records:
            data.append(
                analysis.NumberOfNewUser(
                    id=item.id,
                    role=item.role,
                    created_at=item.created_at
                )
            )

        return analysis.GetNumberOfNewUser(data=data)
    
    async def count_all_number_of_user_by_role(self, db:Session) -> analysis.GetNumberOfAllNewUser:
        records = db.query(User.role, func.count(User.id).label('user_count')).group_by(User.role).all()
        
        data = []
        for item in records:
            data.append(
                analysis.NumberOfAllNewUser(
                    role=item.role,
                    count=item.user_count
                )
            )
        
        return analysis.GetNumberOfAllNewUser(data=data)

    async def percentage_of_different_job_status(self, db:Session) -> analysis.GetNumberOfJobStatus:
        records = db.query(Job.is_hiring, func.count(Job.id).label('status_count')) \
                        .group_by(Job.is_hiring) \
                        .all()
        
        data = []
        for item in records:
            data.append(
                analysis.NumberOfJobStatus(
                    status=item.is_hiring,
                    count=item.status_count
                )
            )
        
        return analysis.GetNumberOfJobStatus(data=data)
    
    async def get_top_recruiters_job_posting (self, db:Session, top_number, time_from, time_to) -> analysis.GetTopRecruiterJobPosting:
        if time_from != 'None' and time_to != 'None':
            records = db.query(Job.recruiter_id, func.concat(User.first_name, ' ', User.last_name).label('full_name'), func.count(Job.id).label('post_count')) \
                            .join(User, Job.recruiter_id == User.id) \
                            .filter(and_(Job.created_at >= time_from, Job.created_at <= time_to)) \
                            .group_by(Job.recruiter_id, 'full_name') \
                            .order_by(desc('post_count')) \
                            .limit(top_number) \
                            .all()
        else:
            records = db.query(Job.recruiter_id, func.concat(User.first_name, ' ', User.last_name).label('full_name'), func.count(Job.id).label('post_count')) \
                            .join(User, Job.recruiter_id == User.id) \
                            .group_by(Job.recruiter_id, 'full_name') \
                            .order_by(func.desc('post_count')) \
                            .limit(top_number) \
                            .all()
        
        data = []
        for item in records:
            data.append(
                analysis.TopRecruiterJobPosting(
                    recruiter_id=item.recruiter_id,
                    full_name=item.full_name,
                    count=item.post_count
                )
            )
        
        return analysis.GetTopRecruiterJobPosting(data=data)
    
    async def get_top_viewed_jobs (self, db:Session, top_number, time_from, time_to) -> analysis.GetTopViewedJob:
        if time_from != 'None' and time_to != 'None':
            records = db.query(Job.common_job_title, func.count(Job.id).label('viewed_count')) \
                            .join(ViewedJob, ViewedJob.job_id == Job.id) \
                            .filter(and_(ViewedJob.view_datetime >= time_from, ViewedJob.view_datetime <= time_to)) \
                            .group_by(Job.common_job_title) \
                            .order_by(desc('viewed_count')) \
                            .limit(top_number) \
                            .all()
        else:
            records = db.query(Job.common_job_title, func.count(Job.id).label('viewed_count')) \
                            .join(ViewedJob, ViewedJob.job_id == Job.id) \
                            .group_by(Job.common_job_title) \
                            .order_by(desc('viewed_count')) \
                            .limit(top_number) \
                            .all()
        
        data = []
        for item in records:
            data.append(
                analysis.TopViewedJob(
                    job_title=item.common_job_title,
                    count=item.viewed_count
                )
            )
        
        return analysis.GetTopViewedJob(data=data)
    
    async def get_top_work_titles(self, db:Session, top_number=10) -> analysis.ListTopWorkTitlesResponse:
        query = db.query(User.work_title, func.count(Candidate.id).label('candidate_count')) \
            .join(Candidate, User.id == Candidate.id) \
            .group_by(User.work_title).order_by(func.count(Candidate.id).desc()).limit(top_number)
        
        records = query.all()
        data = []

        for item in records:
            data.append (
                analysis.TopWorkTitlesResponse (
                    work_title=item.work_title,
                    count=item.candidate_count
                )
            )
        
        return analysis.ListTopWorkTitlesResponse (data=data)
    
    async def get_change_job_salary_by_year(self, db:Session, country_name = 'Vietnam', time=None, time_from=None, time_to=None, job_title = 'Software Engineer') -> analysis.ChangeJobSalaryByYearResponse:
        if "'" in country_name[0]:
            country_name = country_name.replace("'", "")
        if "'" in job_title[0]:
            job_title = job_title.replace("'", "")
        if time is not None and time.lower() != 'none':
            time = time.lower()
            if "'" in time:
                time = time.replace("'", "")
        sql_query = f'''
        SELECT 
            date_trunc('month', ccp_job.updated_at) AS month,
            common_job_title,
            hiring_level,
            ROUND(AVG(
                CASE 
                    WHEN salary_from IS NULL AND salary_to IS NOT NULL THEN salary_to
                    WHEN salary_from IS NOT NULL AND salary_to IS NULL THEN salary_from
                    ELSE (COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0
                END
            )) AS average_salary
        FROM 
            ccp_job
        LEFT JOIN ccp_address ON address_id = ccp_address.id
        LEFT JOIN ccp_city ON ccp_address.city_id = ccp_city.id
        LEFT JOIN ccp_country ON ccp_city.country_id = ccp_country.id
        WHERE 
            common_job_title = '{job_title}' AND country_name = '{country_name}'
        '''
        if time is not None and time.lower() != 'none':
            time = time.lower()
            if "'" in time:
                time = time.replace("'", "")
                sql_query += f'''
                AND ccp_job.updated_at BETWEEN CURRENT_DATE - INTERVAL '1 {time}' AND CURRENT_DATE
                    '''
            elif time_from and time_to and time_from.lower() != 'none' and time_to.lower() != 'none':
                if "'" in time_to or "'" in time_from:
                        time_from = time_from.replace("'", "")
                        time_to =  time_to.replace("'", "")
                sql_query += f'''
                    AND 
                    ccp_job.updated_at >= to_date('{time_from}', 'YYYY/MM') 
                    AND updated_at < to_date('{time_to}', 'YYYY/MM') + interval '1 month'
                    '''        
        sql_query += '''
        GROUP BY 
                    common_job_title, 
                    hiring_level,
                    date_trunc('month', ccp_job.updated_at)
                ORDER BY 
                    date_trunc('month', ccp_job.updated_at) ASC;
        '''
       
        records = db.execute(text(sql_query))

        data = []

        for item in records:
            data.append (
                analysis.ChangeJobSalaryByYearResponse(
                    time=item.month,
                    hiring_level=item.hiring_level,
                    average_salary=item.average_salary
                )
            )
        
        return analysis.ListChangeJobSalaryByYearResponse(data=data)

    async def get_change_job_salary_by_time(self, db:Session, time_from, time_to, level) -> analysis.ListChangeJobSalaryResponse:
        query = db.query (
            func.date_trunc('month', Job.updated_at).label('month'),
            Job.common_job_title,
            func.avg((Job.salary_from + Job.salary_to) / 2).label('salary')
        ).filter (
            Job.updated_at.between(time_from, time_to))

        if level is not None:
            query = query.filter(Job.hiring_level == level)
        
        query = query.group_by (
            func.date_trunc('month', Job.updated_at),
            Job.common_job_title
        ).order_by (
            func.date_trunc('month', Job.updated_at),
            Job.common_job_title
        )

        records = query.all()

        data = []

        for item in records:
            data.append (
                analysis.ChangeJobSalaryResponse (
                    time=item.month,
                    job_title=item.common_job_title,
                    salary=item.salary
                )
            )
        
        return analysis.ListChangeJobSalaryResponse(data=data)

    async def get_number_jobs_by_country(self, db:Session, country_name = 'Vietnam', time = None, time_from=None, time_to=None, job_title= None, level=None) -> analysis.ListNumberofJobsByCountryResponse:
        if "'" not in country_name:
            country_name = f"'{country_name}'"
        sql_query = f'''
                    SELECT 
                hiring_level,
                city_name,
                COUNT(ccp_job.id) as job_number
            FROM 
                ccp_job
            LEFT JOIN ccp_address ON address_id = ccp_address.id
            LEFT JOIN ccp_city ON ccp_address.city_id = ccp_city.id
            LEFT JOIN ccp_country ON ccp_city.country_id = ccp_country.id
            WHERE 
                country_name = {country_name}
            '''
        if time is not None and time.lower() != 'none':
            time = time.lower()
            if "'" in time:
                time = time.replace("'", "")
            sql_query += f'''
             and ccp_job.updated_at BETWEEN CURRENT_DATE - INTERVAL '1 {time}' AND CURRENT_DATE '''
        elif time_from and time_to and time_from.lower() != 'none' and time_to.lower() != 'none':
            if "'" in time_to or "'" in time_from:
                time_from = time_from.replace("'", "")
                time_to =  time_to.replace("'", "")
            sql_query += f'''
             AND 
             ccp_job.updated_at >= to_date('{time_from}', 'YYYY/MM') 
            AND updated_at < to_date('{time_to}', 'YYYY/MM') + interval '1 month'
            '''

        sql_query += '''
        GROUP BY 
                hiring_level,
                city_name; 
                '''

        # Execute the SQL query
        result =  db.execute(text(sql_query))

        # Fetch all the rows from the result
        rows = result.fetchall()
        data = []
        for item in rows:
            data.append(
                analysis.NumberofJobsByCountryResponse(
                    hiring_level=item[0],
                    city=item[1],
                    count=item[2]
                )
            )
        db.close()
        return analysis.ListNumberofJobsByCountryResponse(
            data=data
        )
        

    async def get_list_country(self, db:Session) -> analysis.ListCountryName:
        query = db.query(
            Country.country_name
        )

        records = query.all()
        countries = []

        for item in records:
            countries.append(
                analysis.Country(
                    country_name= item.country_name
                )
            )
        
        return analysis.ListCountryName(
            data=countries
        )

    async def get_list_common_job_title(self, db:Session) -> analysis.ListJobTitle:
        query = db.query(
            Job.common_job_title
        ).filter(Job.common_job_title != 'Other position').distinct()

        records = query.all()
        job_titles = []

        for item in records:
            job_titles.append(
                analysis.JobTitle(
                    job_title=item.common_job_title
                )
            )
        
        return analysis.ListJobTitle(
            data=job_titles
        ) 
