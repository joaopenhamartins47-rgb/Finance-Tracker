from database import db_dependency
from models import Categories
from services.service_classification import DEFAULT_CATEGORY_NAMES
from repositories.repo_categories import save_categories, find_category_by_id, find_all_categories, find_category_by_name, save_category, delete_category_repo
from core.exceptions import CategoryNotFoundError, CategoryExistsError, CategoryIsDefaultError
from schemas import CreateUpdateCategory

def create_default_categories(user_id: int, db: db_dependency):
    categories = [
        Categories(user_id=user_id, name=name, is_default=True,
                   exclude_from_reports=(name == "Pagamentos/Estornos"))
        for name in DEFAULT_CATEGORY_NAMES
    ]
    return save_categories(categories, db)

def get_category(user_id: int, cat_id: int, db:db_dependency):
    cat = find_category_by_id(user_id, cat_id, db)
    if cat is None:
        raise CategoryNotFoundError()
    return cat

def get_all_category(user_id: int, db: db_dependency):
    cat = find_all_categories(user_id, db)
    return cat

def create_category(user_id: int, create_model: CreateUpdateCategory, db: db_dependency):
    cat = find_category_by_name(create_model.name, user_id, db)
    if cat:
        raise CategoryExistsError()
    cat = Categories(name=create_model.name, is_default=False, user_id=user_id)
    return save_category(cat, db)

def update_category(user_id: int, cat_id: int, update_model: CreateUpdateCategory, db: db_dependency):
    cat = find_category_by_id(user_id, cat_id, db)
    if cat is None:
        raise CategoryNotFoundError()
    if cat.is_default:
        raise CategoryIsDefaultError()

    existing = find_category_by_name(update_model.name, user_id, db)
    if existing and existing.id != cat.id:
        raise CategoryExistsError()

    cat.name = update_model.name
    return save_category(cat, db)


def delete_category(user_id: int, cat_id: int, db: db_dependency):
    cat = find_category_by_id(user_id, cat_id, db)
    if cat is None:
        raise CategoryNotFoundError()
    if cat.is_default:
        raise CategoryIsDefaultError()

    return delete_category_repo(cat, db)



