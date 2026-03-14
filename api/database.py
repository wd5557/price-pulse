"""
SQLAlchemy 數據庫配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pricepulse:pricepulse_dev@localhost:5432/pricepulse")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """數據庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
