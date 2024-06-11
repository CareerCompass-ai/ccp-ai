from sqlalchemy.orm import Session

from models.ccp_notifications import Notification


class NotificationsRepository:        
    async def create(self, session: Session, record: dict):
        if record:
            notification = Notification(**record)
            session.add(notification)
            session.flush()
            session.refresh(notification)
            return notification
        return None