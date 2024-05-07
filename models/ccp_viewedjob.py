from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from config.postgres import Base

class ViewedJob(Base):
    __tablename__ = "ccp_recently_viewed_job"
    candidate_id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(Integer, primary_key=True, nullable=False)
    viewed_datetime = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

