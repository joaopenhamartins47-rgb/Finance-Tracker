#Aqui vao ficar as conexoes com o banco

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.configs import settings
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

