from database import db_dependency
from models import Users
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def find_user(username: str, db:db_dependency):
    return db.query(Users).filter(Users.username == username).first()

def create_user(user: Users, db: db_dependency):
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already registered")


