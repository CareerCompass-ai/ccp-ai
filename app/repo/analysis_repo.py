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

        
    
