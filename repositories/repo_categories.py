from database import db_dependency
from models import Categories

def find_category_by_name(name: str, user_id: int, db: db_dependency):
    return db.query(Categories).filter(Categories.name == name, Categories.user_id == user_id).first()

def save_categories(categories, db: db_dependency):
    db.add_all(categories)
    db.commit()
    return categories

def find_category_by_id(user_id: int, cat_id: int, db: db_dependency):
    return db.query(Categories).filter(Categories.user_id == user_id, Categories.id == cat_id).first()

def find_all_categories(user_id: int, db: db_dependency):
    return db.query(Categories).filter(Categories.user_id == user_id).all()

def save_category(category, db: db_dependency):
    db.add(category)
    db.commit()
    return category

def delete_category_repo(category, db: db_dependency):
    db.delete(category)
    db.commit()






