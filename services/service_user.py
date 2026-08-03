from core.security import user_dependency
from core.exceptions import UserNotFoundError
from repositories.users import find_by_username
from models import Users
from database import db_dependency

def get_current_user_from_db(username: str, db: db_dependency) -> Users:
    user = find_by_username(username, db)
    if user is None:
        raise UserNotFoundError()
    return user