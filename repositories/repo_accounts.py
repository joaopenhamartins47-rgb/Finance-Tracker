from database import db_dependency
from models import Accounts
from sqlalchemy.exc import IntegrityError
from core.exceptions import SaveAccountError
from schemas import CreateAccountRequest

def find_by_id(acc_id: int, user_id: int, db: db_dependency):
    return db.query(Accounts).filter(Accounts.id == acc_id, Accounts.user_id == user_id).first()

def find_all(user_id: int, db:db_dependency):
    return db.query(Accounts).filter(Accounts.user_id == user_id).all()

def save_account(account: CreateAccountRequest, db:db_dependency):
    db.add(account)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise SaveAccountError() from e
    db.refresh(account)
    return account

def delete_account(account: Accounts, db: db_dependency):
    db.delete(account)
    db.commit()