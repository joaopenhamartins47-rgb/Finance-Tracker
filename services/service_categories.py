from database import db_dependency
from models import Categories
from services.service_classification import DEFAULT_CATEGORY_NAMES
from repositories.repo_categories import save_categories

def create_default_categories(user_id: int, db: db_dependency):
    categories = [
        Categories(user_id=user_id, name=name, is_default=True,
                   exclude_from_reports=(name == "Pagamentos/Estornos"))
        for name in DEFAULT_CATEGORY_NAMES
    ]
    return save_categories(categories, db)


