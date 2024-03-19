from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_user import User
from app.dto import user

from typing import List, Optional


class UserRepository:
    def __init__(self):
        self.db = SessionLocal()
    def get_by_id(self, id):
        return self.db.query(User).filter(User.id == id).first()