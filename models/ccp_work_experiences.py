from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, Date,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base


class WorkExperience(Base):
    __tablename__ = "ccp_work_experience"

    id = Column(Integer, primary_key=True, nullable=False)
    candidate_id = Column(Integer, nullable=True)
    work_title = Column(String, nullable=True)
    company_id = Column(Integer, nullable=True)
    company_name = Column(String, nullable=True)
    startdate = Column(Date, nullable=True)
    enddate = Column(Date, nullable=True)
    is_engaged = Column(Boolean, default=True)
    detail = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

