from typing import List

from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models.ccp_job import Job
from app.dto import analysis

class AnalysisRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_top_job_titles(self, month=None, year=None) -> List[analysis.GetTopJobTitlesResponse]:

        query = self.db.query(Job.common_job_title, func.count(Job.id).label('job_count'))

        if month is not None:
            query = query.filter(extract('month', Job.updated_at) == month)
        if year is not None:
            query = query.filter(extract('year', Job.updated_at) == year)

        query = query.group_by(Job.common_job_title).order_by(func.count(Job.id).desc())

        records = query.all()

        data = []
        for item in records:
            data.append(
                analysis.GetTopJobTitlesResponse(
                    job_title=item.common_job_title,
                    record=item.job_count
                )
            )
        
        return data
    
    def get_top_leader_salaries(self, limit=5, hiring_level=None, order=1) -> List[analysis.GetTopJobTitlesSalaryResponse]:

        query = self.db.query(Job.id, Job.job_title, Job.job_type, Job.company_type, Job.work_place, func.coalesce((Job.salary_from + Job.salary_to) / 2, 0).label('average_salary'))

        if hiring_level is not None:
            query = query.filter(Job.hiring_level == hiring_level)

        if order == 1:
            query = query.order_by(func.coalesce((Job.salary_from + Job.salary_to) / 2, 0).desc())
        elif order == 2:
            query = query.order_by(func.coalesce((Job.salary_from + Job.salary_to) / 2, 0).asc())

        query = query.limit(limit)

        results = query.all()
        
        data = []
        for item in results:
            data.append (
                analysis.GetTopJobTitlesSalaryResponse(
                    id=item.id,
                    job_title=item.job_title,
                    job_type=item.job_type,
                    company_type=item.company_type,
                    work_place=item.work_place,
                    salary=item.average_salary
                )
            )
        return data

        
    
