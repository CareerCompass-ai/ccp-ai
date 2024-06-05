from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base

class Assistant(Base):
    __tablename__ = "ccp_assistant"

    id = Column(Integer, primary_key=True, nullable=False)
    assistant_id = Column(String, nullable=True)
    file_id = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_url = Column(String, nullable=True)
    time_from = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=True)
    time_to = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=True)
    assistant_name = Column(String, nullable=True)
    thread_id = Column(String, nullable=True)

