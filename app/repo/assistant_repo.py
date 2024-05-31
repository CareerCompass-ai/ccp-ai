from typing import List
from sqlalchemy.orm import Session

from models.ccp_assistant import Assistant

class AssistantRepository:
    async def get_by_file_name(self, db:Session, name):
        return db.query(Assistant).where(Assistant.file_name == name).first()

