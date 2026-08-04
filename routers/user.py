from fastapi import APIRouter
from core.security import user_dependency
from models import Users
from schemas import UserResponse, UserUpdate, UserUpdatePassword
from database import db_dependency
from services.service_user import get_current_user_from_db, update_user, update_user_password

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('/me', response_model=UserResponse)
async def get_user_info(current_user: user_dependency, db: db_dependency) -> Users:
    return get_current_user_from_db(current_user['id'], db)


@router.put("/me", response_model=UserResponse)
async def update_user_info(current_user: user_dependency, update: UserUpdate, db: db_dependency) -> Users:
    return update_user(current_user['id'], update, db)

@router.put("/me/password", response_model=UserResponse)
async def update_password_info(current_user: user_dependency, db: db_dependency, user_verification: UserUpdatePassword) -> Users:
    return update_user_password(current_user['id'], user_verification, db)

