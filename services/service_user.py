from core.exceptions import UserNotFoundError, UsernameAlreadyExists, EmailAlreadyExists
from repositories.users import find_by_username, find_by_email, save_user
from models import Users
from database import db_dependency
from schemas import UserUpdate

def get_current_user_from_db(username: str, db: db_dependency) -> Users:
    user = find_by_username(username, db)
    if user is None:
        raise UserNotFoundError()
    return user

def update_user(username: str, updating_data: UserUpdate, db: db_dependency) -> Users:
    user = get_current_user_from_db(username, db)
    if updating_data.username is not None and updating_data.username != username:
        if find_by_username(updating_data.username, db):
            raise UsernameAlreadyExists()
        user.username = updating_data.username
    if updating_data.email is not None and updating_data.email != user.email:
        if find_by_email(updating_data.email, db):
            raise EmailAlreadyExists()
        user.email = updating_data.email

    return save_user(user, db)

