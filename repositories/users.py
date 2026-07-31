from database import db_dependency
from models import Users
from sqlalchemy.exc import IntegrityError
from core.exceptions import UserAlreadyExistsError

def find_user(username: str, db:db_dependency):
    return db.query(Users).filter(Users.username == username).first()

def find_email(email: str, db:db_dependency):
    return db.query(Users).filter(Users.email == email).first()

def create_user(user: Users, db: db_dependency):
    user_exist = find_user(user.username, db)
    if user_exist:
        raise UserAlreadyExistsError("Username já cadastrado!")
    email_exist = find_email(user.email, db)
    if email_exist:
        raise UserAlreadyExistsError("Email já cadastrado!")

    #Tratamento caso tenha acessos simultâneos com os mesmos dados
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsError('Usuário ou email já cadastrado')


