from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from database import db_dependency
from starlette import status
from schemas import CreateUserRequest, UserResponse
from services.service_auth import create_user_service,login_service

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post("/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(create_user_model: CreateUserRequest, db: db_dependency):
    return create_user_service(create_user_model, db)

@router.post("/token")
def login_to_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_service(db, form_data.username, form_data.password)









