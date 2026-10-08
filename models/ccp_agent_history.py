from sqlalchemy import Column, Integer, String, Float, JSON, Text
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base, engine

class AgentHistory(Base):
    __tablename__ = "ccp_agent_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, index=True, nullable=False)
    candidate_id = Column(Integer, index=True, nullable=True)
    query = Column(String, nullable=True)
    status = Column(String, default="completed")
    summary = Column(Text, nullable=True)
    target_role = Column(String, nullable=True)
    matching_jobs = Column(JSON, nullable=True)
    skill_gaps = Column(JSON, nullable=True)
    roadmap = Column(JSON, nullable=True)
    evaluation_score = Column(Float, nullable=True)
    result_json = Column(JSON, nullable=True)
    steps = Column(JSON, nullable=True)
    iterations = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)


try:
    AgentHistory.__table__.create(bind=engine, checkfirst=True)
except Exception:
    pass
