from sqlalchemy import Boolean, Column, Integer, String, Float
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base

class Job(Base):
    __tablename__ = "ccp_job"

    id = Column(Integer, primary_key=True, nullable=False)
    job_title = Column(String, nullable=True)
    common_job_title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    content_url = Column(String, nullable=True)
    is_hiring = Column(Boolean, default=True)
    opened_date = Column(TIMESTAMP(timezone=True), nullable=True)
    closed_date = Column(TIMESTAMP(timezone=True), nullable=True)
    salary_from = Column(Float, nullable=True)
    salary_to = Column(Float, nullable=True)
    job_type = Column(String, nullable=True)
    work_place = Column(String, nullable=True)
    company_type = Column(String, nullable=True)
    address_id = Column(Integer, nullable=True)
    recruiter_id = Column(Integer, nullable=True)
    applied_count = Column(Integer, nullable=True)
    hiring_level = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

