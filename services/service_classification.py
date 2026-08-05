import re
import unicodedata
from decimal import Decimal
from core.exceptions import TransactionNotFoundError
from repositories.repo_transactions import find_transaction_by_id, save_transaction, find_unclassified_transactions
from repositories.repo_categories import find_category_by_name, save_categories
from models import Categories
from database import db_dependency

CATEGORY_KEYWORDS = {
    "Combustível": ["posto"],
    "Alimentação": ["ifood", "ze delivery", "burger", "pizzaria", "atacadao"],
    "Transporte": ["99 ride", "uber"],
    "Saúde": ["drogaria", "farmacia"],
    "Educação": ["coursera"],
}

DEFAULT_CATEGORY_NAMES = ["Outros", "Pagamentos/Estornos"] + list(CATEGORY_KEYWORDS.keys())

def build_keyword_to_category_map(user_id: int, db: db_dependency) -> dict[str, int]:
    mapping = {}
    for category_name, keywords in CATEGORY_KEYWORDS.items():
        category = find_category_by_name(category_name, user_id, db)
        for kw in keywords:
            mapping[kw] = category.id
    return mapping

def classify_all_transactions(user_id: int, db: db_dependency):
    keyword_to_category = build_keyword_to_category_map(user_id, db)
    payment_category = find_category_by_name("Pagamentos/Estornos", user_id, db)
    fallback_category = find_category_by_name("Outros", user_id, db)

    transactions = find_unclassified_transactions(user_id, db)
    for tx in transactions:
        category_id, is_classified = classify_transaction(
            tx.amount, tx.description, keyword_to_category,
            payment_category.id, fallback_category.id
        )
        tx.category_id = category_id
        tx.is_classified = is_classified

    return save_transaction(transactions, db)

def normalize_text(text: str) -> str: #Deixar tudo em um padrão de texto, minusculo e sem acentuacao
    text = text.lower()
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def classify_transaction(amount: Decimal, description: str, keyword_to_category: dict[str, int], payment_category_id: int, fallback_category_id: int) -> tuple[int, bool]: #Classifica uma funcao especifica
    if amount < 0:
        return payment_category_id, True
    normalized_desc = normalize_text(description)
    for keyword, category_id in keyword_to_category.items():
        pattern = rf'\b{re.escape(normalize_text(keyword))}\b'
        if re.search(pattern, normalized_desc):
            return category_id, True
    return fallback_category_id, False



def reclassify_transaction(transaction_id: int, user_id: int, category_name: str, db: db_dependency): #Criacao de outra categoria pelo usuario
    category = find_category_by_name(category_name, user_id, db)
    if category is None:
        category = Categories(user_id=user_id, name=category_name, is_default=False, exclude_from_reports=False)
        save_categories([category], db)

    tx = find_transaction_by_id(transaction_id, user_id, db)
    if tx is None:
        raise TransactionNotFoundError()

    tx.category_id = category.id
    tx.is_classified = True
    return save_transaction(tx, db)