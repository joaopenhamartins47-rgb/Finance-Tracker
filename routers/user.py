from fastapi import APIRouter
from core.security import user_dependency
from models import Users
from schemas import UserResponse
from database import db_dependency
from services.service_user import get_current_user_from_db

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.get('/me', response_model=UserResponse)
async def get_user_info (current_user: user_dependency, db: db_dependency) -> Users:
    return get_current_user_from_db(current_user['username'], db)