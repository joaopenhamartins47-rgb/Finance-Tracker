from database import db_dependency
from models import Users
from sqlalchemy.exc import IntegrityError
from core.exceptions import UserAlreadyExistsError

def find_by_username(username: str, db:db_dependency):
    return db.query(Users).filter(Users.username == username).first()

def find_by_email(email: str, db:db_dependency):
    return db.query(Users).filter(Users.email == email).first()

def save_user(user: Users, db: db_dependency):
    #Tratamento caso tenha acessos simultâneos com os mesmos dados
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsError()
    db.refresh(user)
    return user


