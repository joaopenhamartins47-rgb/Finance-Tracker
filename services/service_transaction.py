import io
from database import db_dependency
from models import Transactions
from repositories.repo_transactions import create_transaction, find_all_transaction, find_transaction_by_id, save_transaction, delete_transaction, create_transactions_bulk, find_existing_hashes_in
from repositories.repo_accounts import find_acc_by_id
from repositories.repo_categories import find_category_by_id, find_category_by_name
from services.service_classification import classify_transaction, build_keyword_to_category_map
from schemas import CreateTransactionRequest, UpdateTransactionRequest
from core.exceptions import TransactionNotFoundError, AccountNotFoundError, CategoryNotFoundError
from fastapi import UploadFile
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert
import hashlib
import pandas as pd



def compute_import_hash(date: str, title: str, amount: Decimal) -> str:
    raw = f"{date}{title}{amount}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def import_csv(user_id: int, account_id: int, file: io.BytesIO, db: db_dependency) -> dict:
    acc = find_acc_by_id(account_id, user_id, db)
    if not acc:
        raise AccountNotFoundError()

    keyword_to_category = build_keyword_to_category_map(user_id, db)
    payment_category = find_category_by_name("Pagamentos/Estornos", user_id, db)
    fallback_category = find_category_by_name("Outros", user_id, db)
    if payment_category is None or fallback_category is None:
        raise CategoryNotFoundError("Categorias padrão não encontradas — rode create_default_categories antes de importar.")

    df = pd.read_csv(file)
    df["amount"] = (
        df["amount"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("- ", "-", regex=False)
        .apply(Decimal)
    )
    df["parsed_date"] = pd.to_datetime(df["date"]).dt.date

    rows = list(df.itertuples(index=False))
    row_hashes = [compute_import_hash(str(r.date), str(r.title), r.amount) for r in rows]

    existing_hashes = find_existing_hashes_in(user_id, row_hashes, db)

    to_insert = []
    seen_in_batch = set()
    imported = 0
    duplicated = 0

    for row, raw_hash in zip(rows, row_hashes):
        if raw_hash in existing_hashes or raw_hash in seen_in_batch:
            duplicated += 1
            continue

        description = str(row.title)
        category_id, is_classified = classify_transaction(
            row.amount, description, keyword_to_category,
            payment_category.id, fallback_category.id
        )

        to_insert.append({
            "user_id": user_id,
            "account_id": account_id,
            "category_id": category_id,
            "is_classified": is_classified,
            "transaction_date": row.parsed_date,
            "description": description,
            "amount": row.amount,
            "raw_import_hash": raw_hash,
        })
        seen_in_batch.add(raw_hash)
        imported += 1

    create_transactions_bulk(to_insert, db)
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






