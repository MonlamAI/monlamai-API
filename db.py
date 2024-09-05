from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
import os 

from dotenv import load_dotenv

load_dotenv(override=True) 

database_url=os.getenv("DATABASE_URL")
engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base=declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()