from database import db_dependency
from models import Transactions


def find_transaction_by_id(transaction_id: int, user_id: int, db: db_dependency):
    return db.query(Transactions).filter(Transactions.id == transaction_id, Transactions.user_id == user_id).first()

def save_transaction(transaction: list[Transactions], db: db_dependency):
    db.commit()
    return transaction

def find_unclassified_transactions(user_id: int, db: db_dependency):
    return db.query(Transactions).filter(Transactions.user_id == user_id, Transactions.is_classified == False).all()