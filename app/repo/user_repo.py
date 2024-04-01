from config.postgres import SessionLocal

from models.ccp_user import User

class UserRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(User).filter(User.id == id).first()