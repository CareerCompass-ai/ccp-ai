from sqlalchemy import Column, Integer
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base


class Application(Base):
    __tablename__ = "ccp_application"

    resume_id = Column(Integer, primary_key=True, nullable=False)
    job_id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    status = Column(Integer, nullable=True)

