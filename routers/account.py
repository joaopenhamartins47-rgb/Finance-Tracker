from fastapi import APIRouter
from database import db_dependency
from core.security import user_dependency
from services.service_account import get_user_accounts, get_user_account_id, create_account, edit_account, del_account
from schemas import CreateAccountRequest, AccountResponse, UpdateAccountRequest
from starlette import status

router = APIRouter(
    prefix='/account',
    tags=['accounts']
)

@router.get("/", response_model=list[AccountResponse])
async def get_user_accounts_endpoint (user: user_dependency, db: db_dependency):
    return get_user_accounts(user['id'], db)

@router.get("/{acc_id}", response_model=AccountResponse)
async def get_user_account_id_endpoint(acc_id: int, user: user_dependency, db: db_dependency):
    return get_user_account_id(acc_id, user['id'], db)


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account_endpoint(user: user_dependency, db: db_dependency, acc_model: CreateAccountRequest):
    return create_account(user['id'], acc_model, db)

@router.put("/{acc_id}", response_model=AccountResponse)
async def edit_account_endpoint(acc_id:int, user: user_dependency, db: db_dependency, acc_model: UpdateAccountRequest):
    return edit_account(acc_id, user['id'], acc_model, db)


@router.delete("/{acc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_endpoint(user: user_dependency, db:db_dependency, acc_id: int):
    del_account(acc_id, user['id'], db)
