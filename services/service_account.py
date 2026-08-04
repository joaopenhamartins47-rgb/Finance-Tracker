from database import db_dependency
from repositories.repo_accounts import find_all, find_by_id, save_account, delete_account
from core.exceptions import AccountNotFoundError
from schemas import CreateAccountRequest, UpdateAccountRequest
from models import Accounts

def get_user_accounts(user_id: int, db: db_dependency):
    return find_all(user_id, db)

def get_user_account_id(acc_id: int, user_id: int, db:db_dependency):
    acc = find_by_id(acc_id, user_id, db)
    if acc is None:
        raise AccountNotFoundError()
    return acc


def create_account(user_id: int, account_request: CreateAccountRequest, db: db_dependency):
    account_model = Accounts(
        user_id=user_id,
        nome=account_request.nome,
        account_type=account_request.account_type
    )
    return save_account(account_model, db)

def edit_account(acc_id: int, user_id: int, acc_put: UpdateAccountRequest, db:db_dependency):
    account = find_by_id(acc_id, user_id, db)
    if account is None:
        raise AccountNotFoundError()
    if acc_put.nome is not None:
        account.nome=acc_put.nome
    if acc_put.account_type is not None:
        account.account_type=acc_put.account_type
    return save_account(account, db)

def del_account(acc_id: int, user_id: int, db: db_dependency):
    acc = find_by_id(acc_id, user_id, db)
    if acc is None:
        raise AccountNotFoundError()
    delete_account(acc, db)
