from fastapi import Depends
from core.security import get_current_user
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session




user_dependency = Annotated[dict, Depends(get_current_user)]
