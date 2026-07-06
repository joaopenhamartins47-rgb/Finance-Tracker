from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from typing import Annotated

from models import Users

from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from dependencies import db_dependency
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)



#Criar o usuario
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.post("/create-user")
def create_user(create_user_model: CreateUserRequest, db: db_dependency):
    create_new_user = Users(
        username=create_user_model.username,
        email=create_user_model.email,
        hashed_password=bcrypt_context.hash(create_user_model.hashed_password)
    )
    db.add(create_new_user)
    db.commit()
#Autenticar usuario
def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

#Preciso do secret_key e do algorithm pra gerar o token

import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

#Gerar o token

from jose import jwt, JWTError

def create_user_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


#Acessar o token
auth2bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

from starlette import status

def get_current_user(token: Annotated[str, Depends(auth2bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

@router.post("/token")
def login_to_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

    token = create_user_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}









