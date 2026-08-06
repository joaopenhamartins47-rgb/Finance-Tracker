from fastapi import APIRouter

from core.security import user_dependency
from database import db_dependency
from schemas import CategoriesResponse, CreateUpdateCategory
from services.service_categories import get_category, get_all_category, create_category, update_category, delete_category
from starlette import status


router = APIRouter(
    prefix="/category",
    tags=['Category']
)

@router.get("/{cat_id}", response_model=CategoriesResponse)
async def find_category_endpoint(current_user: user_dependency, cat_id: int, db: db_dependency):
    return get_category(current_user['id'], cat_id, db)

@router.get("/", response_model=list[CategoriesResponse])
async def get_all_cat_endpoint(current_user: user_dependency, db: db_dependency):
    return get_all_category(current_user['id'], db)

@router.post("/", response_model=CategoriesResponse, status_code=status.HTTP_201_CREATED)
async def create_cat_endpoint(current_user: user_dependency, db: db_dependency, create_model: CreateUpdateCategory):
    return create_category(current_user['id'], create_model, db)

@router.put("/{cat_id}", response_model=CategoriesResponse)
async def update_category_endpoint(current_user: user_dependency,cat_id: int, update_model: CreateUpdateCategory, db: db_dependency):
    return update_category(current_user['id'], cat_id, update_model, db)

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(cat_id: int, current_user: user_dependency, db: db_dependency):
    return delete_category(current_user['id'], cat_id, db)
