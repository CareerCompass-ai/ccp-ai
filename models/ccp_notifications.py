from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Notification(Base):
    __tablename__ = "ccp_notifications"

    id = Column(Integer, primary_key=True, nullable=False)
    recruiter_id = Column(Integer, nullable=False)
    candidate_id = Column(Integer, nullable=False)
    job_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
