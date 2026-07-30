from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from models import Users
from fastapi.security import OAuth2PasswordRequestForm
from database import db_dependency
from core.configs import settings
from starlette import status
from core.security import create_user_token, authenticate_user, bcrypt_context
from schemas import CreateUserRequest, UserResponse
from repositories.users import create_user

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)





@router.post("/create-user", response_model=UserResponse)
def create_user_endpoint(create_user_model: CreateUserRequest, db: db_dependency):
    create_new_user = Users(
        username=create_user_model.username,
        email=create_user_model.email,
        hashed_password=bcrypt_context.hash(create_user_model.password)
    )
    create_user(create_new_user, db)
    db.refresh(create_new_user)
    return create_new_user



@router.post("/token")
def login_to_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

    token = create_user_token(user.username, user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE))

    return {'access_token': token, 'token_type': 'bearer'}









