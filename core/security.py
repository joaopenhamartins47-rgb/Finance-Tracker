from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from core.configs import settings
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from starlette import status
from database import db_dependency
from repositories.users import find_user

#Acessar o token
auth2bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def create_user_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_current_user(token: Annotated[str, Depends(auth2bearer)]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

#Autenticar usuario
def authenticate_user(username: str, password: str, db: db_dependency):
    user = find_user(username, db)
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user