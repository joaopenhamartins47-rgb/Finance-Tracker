from fastapi import APIRouter
from core.security import user_dependency
from models import Users
from schemas import UserResponse, UserUpdate
from database import db_dependency
from services.service_user import get_current_user_from_db, update_user

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('/me', response_model=UserResponse)
async def get_user_info(current_user: user_dependency, db: db_dependency) -> Users:
    return get_current_user_from_db(current_user['username'], db)


@router.put("/me", response_model=UserResponse)
async def update_user_info(current_user: user_dependency, update: UserUpdate, db: db_dependency):
    return update_user(current_user['username'], update, db)

