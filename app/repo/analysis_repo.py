from typing import List

from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, and_
from models.ccp_job import Job
from models.ccp_jobtag import JobTag
from app.dto import analysis
from models.ccp_tag import Tag
from models.ccp_user import User
from models.ccp_viewedjob import ViewedJob
class AnalysisRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_top_job_titles(self, month, year) -> analysis.GetTopJobTitlesResponse:

        records = self.db.query(Job.common_job_title, func.count(Job.id).label('job_count')) \
                        .filter(extract('month', Job.updated_at ) == month ) \
                        .filter(extract('year', Job.updated_at) == year) \
                        .group_by(Job.common_job_title) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.TopJobTitlesResponse(
                    job_title=item.common_job_title,
                    count=item.job_count
                )
            )
        
        return analysis.GetTopJobTitlesResponse(data=data)
    
    def get_top_skills (self, top_number) -> analysis.GetTopSkillResponse:
        records = self.db.query(Tag.id, Tag.tag_name, func.count(Tag.id).label('skill_count')) \
                        .join(JobTag, Tag.id == JobTag.tag_id) \
                        .group_by(Tag.id, Tag.tag_name) \
                        .order_by(desc('skill_count')) \
                        .limit(top_number) \
                        .all()
        data = []
        for item in records:
            data.append(
                analysis.TopSkillResponse(
                    id=item.id,
                    skill=item.tag_name,
                    count=item.skill_count
                )
            )
        
        return analysis.GetTopSkillResponse(data=data)        
    
    def number_of_company_type (self) -> analysis.GetNumberOfCompanyTypeResponse:
        records = self.db.query(Job.company_type, func.count(Job.id).label('company_type_count')).group_by(Job.company_type).all()
        data = []
        for item in records:
            data.append(
                analysis.NumberOfCompanyTypeResponse(
                    company_type=item.company_type,
                    count = item.company_type_count
                )
            )    

        return analysis.GetNumberOfCompanyTypeResponse(data=data)
    
    def get_number_of_new_user(self, time_from, time_to) -> analysis.GetNumberOfNewUser:

        records = self.db.query(User.id, User.role, User.created_at) \
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
    
    def count_all_number_of_user_by_role(self) -> analysis.GetNumberOfAllNewUser:

        records = self.db.query(User.role, func.count(User.id).label('user_count')).group_by(User.role).all()
        data = []
        for item in records:
            data.append(
                analysis.NumberOfAllNewUser(
                    role=item.role,
                    count=item.user_count
                )
            )
        
        return analysis.GetNumberOfAllNewUser(data=data)

    def percentage_of_different_job_status(self) -> analysis.GetNumberOfJobStatus:

        records = self.db.query(Job.is_hiring, func.count(Job.id).label('status_count')) \
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
    

    def get_top_recruiters_job_posting (self, top_number, time_from, time_to) -> analysis.GetTopRecruiterJobPosting:
        if time_from != 'None' and time_to != 'None':
            records = self.db.query(Job.recruiter_id, func.concat(User.first_name, ' ', User.last_name).label('full_name'), func.count(Job.id).label('post_count')) \
                            .join(User, Job.recruiter_id == User.id) \
                            .filter(and_(Job.created_at >= time_from, Job.created_at <= time_to)) \
                            .group_by(Job.recruiter_id, 'full_name') \
                            .order_by(desc('post_count')) \
                            .limit(top_number) \
                            .all()
        else:
            records = self.db.query(Job.recruiter_id, func.concat(User.first_name, ' ', User.last_name).label('full_name'), func.count(Job.id).label('post_count')) \
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
    
    def get_top_viewed_jobs (self, top_number, time_from, time_to) -> analysis.GetTopViewedJob:
        if time_from != 'None' and time_to != 'None':
            records = self.db.query(Job.common_job_title, func.count(Job.id).label('viewed_count')) \
                            .join(ViewedJob, ViewedJob.job_id == Job.id) \
                            .filter(and_(ViewedJob.view_datetime >= time_from, ViewedJob.view_datetime <= time_to)) \
                            .group_by(Job.common_job_title) \
                            .order_by(desc('viewed_count')) \
                            .limit(top_number) \
                            .all()
        else:
            records = self.db.query(Job.common_job_title, func.count(Job.id).label('viewed_count')) \
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
    
    