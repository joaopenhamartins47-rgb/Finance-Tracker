from database import db_dependency
from models import Transactions
from sqlalchemy import insert



def find_transaction_by_id(transaction_id: int, user_id: int, db: db_dependency):
    return db.query(Transactions).filter(Transactions.id == transaction_id, Transactions.user_id == user_id).first()

def save_transaction(transaction: list[Transactions], db: db_dependency):
    db.commit()
    return transaction

def find_unclassified_transactions(user_id: int, db: db_dependency):
    return db.query(Transactions).filter(Transactions.user_id == user_id, Transactions.is_classified == False).all()

def find_all_transaction(user_id: int, db:db_dependency):
    return db.query(Transactions).filter(Transactions.user_id == user_id).all()

def create_transaction(transaction: Transactions, db:db_dependency):
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def delete_transaction(transaction: Transactions, db: db_dependency):
    db.delete(transaction)
    db.commit()

def create_transactions_bulk(rows: list[dict], db: db_dependency) -> None:
    if not rows:
        return
    db.execute(insert(Transactions), rows)
    db.commit()

def find_existing_hashes_in(user_id: int, hashes: list[str], db: db_dependency) -> set[str]:
    rows = db.query(Transactions.raw_import_hash).filter(Transactions.user_id == user_id,Transactions.raw_import_hash.in_(hashes)).all()
    return {h for (h,) in rows}