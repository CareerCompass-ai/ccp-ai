from typing import List

from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from models.ccp_job import Job
from models.ccp_jobtag import JobTag
from app.dto import analysis
from models.ccp_tag import Tag
from models.ccp_user import User
class AnalysisRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_top_job_titles(self, month, year) -> List[analysis.GetTopJobTitlesResponse]:

        records = self.db.query(Job.common_job_title, func.count(Job.id).label('job_count')) \
                        .filter(extract('month', Job.updated_at ) == month ) \
                        .filter(extract('year', Job.updated_at) == year) \
                        .group_by(Job.common_job_title) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetTopJobTitlesResponse(
                    job_title=item.common_job_title,
                    count=item.job_count
                )
            )
        
        return data
    
    def get_top_skills (self, top_number) -> List[analysis.GetTopSkillResponse]:
        records = self.db.query(Tag.tag_name, func.count(Tag.id).label('skill_count')) \
                        .join(JobTag, Tag.id == JobTag.tag_id) \
                        .group_by(JobTag.tag_id) \
                        .order_by(desc('skill_count')) \
                        .limit(top_number) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetTopSkillResponse(
                    job_title=item.tag_name,
                    count=item.skill_count
                )
            )
        
        return data        
    
    def number_of_company_type (self) -> List[analysis.GetNumberOfCompanyTypeResponse]:
        records = self.db.query(Job.company_type, func.count(Job.id).label('company_type_count')).group_by(Job.company_type).all()
        data = []
        for item in records:
            data.append(
                analysis.GetNumberOfCompanyTypeResponse(
                    company_type=item.company_type,
                    count = item.company_type_count
                )
            )    

        return data
    