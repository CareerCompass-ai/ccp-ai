from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, Date,
                        String)
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base


class Project(Base):
    __tablename__ = "ccp_project"

    id = Column(Integer, primary_key=True, nullable=False)
    candidate_id = Column(Integer, nullable=False)
    project_name = Column(String, nullable=True)
    startdate = Column(Date, nullable=True)
    enddate = Column(Date, nullable=True)
    is_working = Column(Boolean, default=True)
    detail = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

