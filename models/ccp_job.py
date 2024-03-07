from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from config.postgres import Base

class Job(Base):
    __tablename__ = "ccp_job"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    content_url = Column(String)
    is_hiring = Column(Boolean, default=True)
    opened_date = Column(TIMESTAMP(timezone=True),)
    closed_date = Column(TIMESTAMP(timezone=True),)
    salary_from = Column(Float)
    salary_to = Column(Float)
    job_type = Column(Integer)
    company_type = Column(Integer)

    created_at = Column(TIMESTAMP(timezone=True),)
    updated_at = Column(TIMESTAMP(timezone=True),)

