from typing import List
from sqlalchemy.orm import Session

from models.ccp_assistant import Assistant
from typing import List, Optional
from app.dto import assistant
from models.ccp_assistant import Assistant

class AssistantRepository:
    async def get_by_file_name(self, db:Session, name):
        return db.query(Assistant).where(Assistant.file_name == name).first()

    async def create(self, session: Session, input: Optional[assistant.AssistantBase]) -> Assistant:
        if input:
            record = Assistant(**input.model_dump())
            session.add(record)
            session.flush()  
            session.refresh(record)  

            return record
        
        return None
    
