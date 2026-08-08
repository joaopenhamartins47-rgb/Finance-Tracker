from database import db_dependency
from models import Transactions
from repositories.repo_transactions import create_transaction, find_all_transaction, find_transaction_by_id, save_transaction, delete_transaction
from repositories.repo_accounts import find_acc_by_id
from repositories.repo_categories import find_category_by_id
from schemas import CreateTransactionRequest, UpdateTransactionRequest
from core.exceptions import TransactionNotFoundError, AccountNotFoundError, CategoryNotFoundError

def get_all_transactions(user_id: int, db: db_dependency) -> list[Transactions]:
    tx = find_all_transaction(user_id, db)
    return tx

def get_transaction_by_id(user_id: int, tx_id: int, db: db_dependency):
    tx = find_transaction_by_id(tx_id, user_id, db)
    if not tx:
        raise TransactionNotFoundError()
    return tx

def create_tx(user_id: int, create_model: CreateTransactionRequest, db: db_dependency):
    acc = find_acc_by_id(create_model.account_id, user_id, db)
    if not acc:
        raise AccountNotFoundError()
    cat = find_category_by_id(user_id, create_model.category_id, db)
    if not cat:
        raise CategoryNotFoundError()
    tx = Transactions(user_id=user_id, **create_model.model_dump())
    return create_transaction(tx, db)

def update_tx(user_id: int, tx_id: int, update_model: UpdateTransactionRequest, db: db_dependency):
    tx = find_transaction_by_id(tx_id, user_id, db)
    if tx is None:
        raise TransactionNotFoundError()

    update_data = update_model.model_dump(exclude_unset=True) # Esse argumento só retorna os valores realmente válidos que foram digitados pelo cliente

    if "account_id" in update_data:
        acc = find_acc_by_id(update_data["account_id"], user_id, db)
        if not acc:
            raise AccountNotFoundError()

    if "category_id" in update_data:
        cat = find_category_by_id(user_id, update_data["category_id"], db)
        if not cat:
            raise CategoryNotFoundError()

    for field, value in update_data.items():
        setattr(tx, field, value) # Define os atributos pra cada

    return save_transaction(tx, db)

def delete_tx(user_id: int, tx_id: int, db: db_dependency):
    tx = find_transaction_by_id(tx_id, user_id, db)
    if not tx:
        raise TransactionNotFoundError()
    return delete_transaction(tx, db)





