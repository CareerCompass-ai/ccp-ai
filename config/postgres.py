from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlalchemy
import sqlalchemy.orm

from constant.config import DATABASE_URL

MAX_CONNECTIONS = 20

engine = create_engine(DATABASE_URL, pool_size=MAX_CONNECTIONS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
thread_local_session = scoped_session(SessionLocal)

Base = sqlalchemy.orm.declarative_base()

class PostgresDB:
    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
