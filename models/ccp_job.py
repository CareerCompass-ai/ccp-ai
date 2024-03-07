from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from config.postgres import Base

class Job(Base):
    __tablename__ = "ccp_job"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    content_url = Column(String, nullable=True)
    is_hiring = Column(Boolean, default=True)
    opened_date = Column(TIMESTAMP(timezone=True), nullable=True)
    closed_date = Column(TIMESTAMP(timezone=True), nullable=True)
    salary_from = Column(Float, nullable=True)
    salary_to = Column(Float, nullable=True)
    job_type = Column(Integer, nullable=True)
    company_type = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

