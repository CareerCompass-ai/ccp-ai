from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base


class Candidate(Base):
    __tablename__ = "ccp_candidate"

    id = Column(Integer, primary_key=True, nullable=False)
    year_of_experience = Column(Integer, nullable=True)
    open_to_work = Column(Boolean, nullable=True)
    self_introduction = Column(String, nullable=True)
    level = Column(String, nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

