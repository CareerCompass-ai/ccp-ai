from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, Date,
                        String)
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config.postgres import Base


class Certificate(Base):
    __tablename__ = "ccp_certificate"

    id = Column(Integer, primary_key=True, nullable=False)
    candidate_id = Column(Integer, nullable=False)
    certificate_name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    link = Column(String, nullable=True)
    detail = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

