from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models import ccp_job
from models.ccp_job import Job

from app.dto import job

from typing import List, Optional


class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Job).filter(Job.id == id).first()