from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from constant.config import DATABASE_URL

MAX_CONNECTIONS = 20

engine = create_engine(DATABASE_URL, pool_size=MAX_CONNECTIONS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class PostgresDB:
    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
