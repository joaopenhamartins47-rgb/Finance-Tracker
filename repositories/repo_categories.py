from database import db_dependency
from models import Categories

def find_category_by_name(name: str, user_id: int, db: db_dependency):
    return db.query(Categories).filter(Categories.name == name, Categories.user_id == user_id).first()

def save_categories(categories: list[Categories], db: db_dependency):
    db.add_all(categories)
    db.commit()
    return categories



