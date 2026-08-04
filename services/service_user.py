from core.exceptions import UserNotFoundError, UsernameAlreadyExists, EmailAlreadyExists, InvalidCredentialsError
from core.security import verify_password, get_password_hash
from repositories.users import find_by_id, find_by_email, save_user, find_by_username
from models import Users
from database import db_dependency
from schemas import UserUpdate, UserUpdatePassword

def get_current_user_from_db(user_id, db: db_dependency) -> Users:
    user = find_by_id(user_id, db)
    if user is None:
        raise UserNotFoundError()
    return user

def update_user(user_id: int, updating_data: UserUpdate, db: db_dependency) -> Users:
    user = get_current_user_from_db(user_id, db)
    if updating_data.username is not None and updating_data.username != user.username:
        if find_by_username(updating_data.username, db):
            raise UsernameAlreadyExists()
        user.username = updating_data.username
    if updating_data.email is not None and updating_data.email != user.email:
        if find_by_email(updating_data.email, db):
            raise EmailAlreadyExists()
        user.email = updating_data.email

    return save_user(user, db)

def update_user_password(user_id: int, user_verification: UserUpdatePassword, db: db_dependency) -> Users:
    user = get_current_user_from_db(user_id, db)
    if not verify_password(user_verification.password, user.hashed_password):
        raise InvalidCredentialsError()
    user.hashed_password = get_password_hash(user_verification.new_password)
    return save_user(user, db)




