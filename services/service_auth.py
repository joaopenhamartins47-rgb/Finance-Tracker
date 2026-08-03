from datetime import timedelta
from database import db_dependency
from models import Users
from schemas import CreateUserRequest
from core.configs import settings
from core.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from core.security import get_password_hash, verify_password, create_user_token
from repositories.users import find_by_email, find_by_username, save_user


def create_user_service(create_user_model: CreateUserRequest, db: db_dependency) -> Users:
    if find_by_username(create_user_model.username, db):
        raise UserAlreadyExistsError()

    if find_by_email(create_user_model.email, db):
        raise UserAlreadyExistsError()

    create_new_user = Users(
        username=create_user_model.username,
        email=create_user_model.email,
        hashed_password=get_password_hash(create_user_model.password)
    )
    return save_user(create_new_user, db)


def login_service(db: db_dependency, username: str, password: str) -> dict[str, str]:
    user = find_by_username(username, db)

    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()

    token = create_user_token(
        user.username,
        user.id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    )
    return {'access_token': token, 'token_type': 'bearer'}