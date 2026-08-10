from database import db_dependency
from models import Transactions
from repositories.repo_transactions import create_transaction, find_all_transaction, find_transaction_by_id, save_transaction, delete_transaction
from repositories.repo_accounts import find_acc_by_id
from repositories.repo_categories import find_category_by_id, find_category_by_name
from services.service_classification import classify_transaction, build_keyword_to_category_map
from schemas import CreateTransactionRequest, UpdateTransactionRequest
from core.exceptions import TransactionNotFoundError, AccountNotFoundError, CategoryNotFoundError
from fastapi import UploadFile
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
import hashlib
import pandas as pd


def compute_import_hash(date: str, title: str, amount: Decimal) -> str:
    raw = f"{date}{title}{amount}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def import_csv(user_id: int, account_id: int, file: UploadFile, db: db_dependency) -> dict:
    acc = find_acc_by_id(account_id, user_id, db)
    if not acc:
        raise AccountNotFoundError()

    # Contexto de classificação montado UMA vez, fora do loop
    keyword_to_category = build_keyword_to_category_map(user_id, db)
    payment_category = find_category_by_name("Pagamentos/Estornos", user_id, db)
    fallback_category = find_category_by_name("Outros", user_id, db)
    if payment_category is None or fallback_category is None:
        raise CategoryNotFoundError()

    df = pd.read_csv(file.file)

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("- ", "-", regex=False)
        .apply(Decimal)
    )

    imported = 0
    duplicated = 0

    for _, row in df.iterrows():
        amount = row["amount"]
        description = str(row["title"])
        raw_date_str = str(row["date"])

        # Converte a string de data para objeto date
        parsed_date = pd.to_datetime(raw_date_str).date()

        raw_hash = compute_import_hash(raw_date_str, description, amount)

        category_id, is_classified = classify_transaction(
            amount, description, keyword_to_category,
            payment_category.id, fallback_category.id
        )

        tx = Transactions(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            is_classified=is_classified,
            transaction_date=parsed_date,  # Nome exato da coluna no seu model Transactions
            description=description,
            amount=amount,
            raw_import_hash=raw_hash,
        )

        try:
            create_transaction(tx, db)
            imported += 1
        except IntegrityError:
            db.rollback()
            duplicated += 1

    return {"importadas": imported, "duplicadas": duplicated}

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






