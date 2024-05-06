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
        records = self.db.query(Tag.id, Tag.tag_name, func.count(Tag.id).label('skill_count')) \
                        .join(JobTag, Tag.id == JobTag.tag_id) \
                        .group_by(Tag.id, Tag.tag_name) \
                        .order_by(desc('skill_count')) \
                        .limit(top_number) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetTopSkillResponse(
                    id=item.id,
                    skill=item.tag_name,
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
    
    def get_number_of_new_user(self, time_from, time_to) -> List[analysis.GetNumberOfNewUser]:

        records = self.db.query(User.role, User.created_at) \
                        .filter(User.created_at >= time_from and User.created_at <= time_to ) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetNumberOfNewUser(
                    role=item.role,
                    created_at=item.created_at
                )
            )
        
        return data
    
    def get_all_number_of_user(self) -> List[analysis.GetNumberOfNewUser]:

        records = self.db.query(User.role, User.created_at) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetNumberOfNewUser(
                    role=item.role,
                    created_at=item.created_at
                )
            )
        
        return data

    def percentage_of_different_job_status(self) -> List[analysis.GetNumberOfJobStatus]:

        records = self.db.query(Job.is_hiring, func.count(Job.id).label('status_count')) \
                        .group_by(Job.is_hiring) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetNumberOfJobStatus(
                    status=item.is_hiring,
                    count=item.status_count
                )
            )
        
        return data
    

    def get_top_recruiters_job_posting (self, top_number, time_from, time_to) -> List[analysis.GetTopRecruiterJobPosting]:
        records = self.db.query(Job.recruiter_id, User.first_name + ' ' + User.last_name, func.count(Job.id).label('post_count')) \
                        .join(User, Job.recruiter_id == User.id) \
                        .filter(Job.created_at >= time_from and Job.created_at <= time_to ) \
                        .group_by(Job.recruiter_id) \
                        .order_by(desc('post_count')) \
                        .limit(top_number) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.GetTopRecruiterJobPosting(
                    recruiter_id=item.tag_name,
                    full_name=item.first_name + ' ' + item.last_name,
                    count=item.post_count
                )
            )
        
        return data  
