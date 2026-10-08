import traceback
from typing import List, Optional
from sqlalchemy.orm import Session
from models.ccp_agent_history import AgentHistory
from pkg.logging import logger

class AgentHistoryRepository:
    def save(self, db: Session, history_data: dict) -> Optional[AgentHistory]:
        try:
            entry = AgentHistory(**history_data)
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return entry
        except Exception:
            db.rollback()
            logger.error(f"[AgentHistoryRepo] Failed to save history: {traceback.format_exc()}")
            return None

    def get_by_task_id(self, db: Session, task_id: str) -> Optional[AgentHistory]:
        try:
            return db.query(AgentHistory).filter(AgentHistory.task_id == task_id).first()
        except Exception:
            logger.error(f"[AgentHistoryRepo] Failed to get task {task_id}: {traceback.format_exc()}")
            return None

    def list_by_candidate(self, db: Session, candidate_id: int, limit: int = 20, offset: int = 0) -> List[AgentHistory]:
        try:
            return (
                db.query(AgentHistory)
                .filter(AgentHistory.candidate_id == candidate_id)
                .order_by(AgentHistory.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
        except Exception:
            logger.error(f"[AgentHistoryRepo] Failed to list for candidate {candidate_id}: {traceback.format_exc()}")
            return []
