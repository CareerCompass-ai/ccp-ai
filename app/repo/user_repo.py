from typing import Optional
from sqlalchemy.orm import Session

from models.ccp_user import User


class UserRepository:
    async def get_by_id(self, db:Session, id) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()