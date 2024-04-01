from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from config.postgres import Base

class Resume(Base):
    __tablename__ = "ccp_resume"

    id = Column(Integer, primary_key=True, nullable=False)
    candidate_id = Column(Integer, nullable=True)
    resume_name = Column(String, nullable=True) 
    content = Column(String, nullable=True)
    resume_link = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

