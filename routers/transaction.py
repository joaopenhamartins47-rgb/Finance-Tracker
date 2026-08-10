from fastapi import APIRouter, UploadFile, Form, File
from services.service_transaction import create_tx, delete_tx, get_all_transactions, get_transaction_by_id, update_tx, import_csv
from services.service_classification import classify_all_transactions
from database import db_dependency
from core.security import user_dependency
from schemas import CreateTransactionRequest, UpdateTransactionRequest, TransactionResponse, ImportcsvResponse, ClassifyPendingResponse
from starlette import status


router = APIRouter(
    prefix="/transactions",
    tags=['Transactions']
)

@router.get("/{tx_id}", response_model=TransactionResponse)
async def get_transaction_id_endpoint(tx_id: int, user: user_dependency, db: db_dependency):
    return get_transaction_by_id(user['id'], tx_id, db)

@router.get("/", response_model=list[TransactionResponse])
async def get_all_transactions_endpoint(user: user_dependency, db: db_dependency):
    return get_all_transactions(user['id'], db)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
async def create_transaction_endpoint(user: user_dependency, create_model: CreateTransactionRequest, db: db_dependency):
    return create_tx(user['id'], create_model, db)

@router.put("/{tx_id}", response_model=TransactionResponse)
async def update_transactions_endpoint(user: user_dependency, update_model: UpdateTransactionRequest, tx_id: int, db: db_dependency):
    return update_tx(user['id'], tx_id, update_model, db)

@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transactions_endpoint(user: user_dependency, tx_id: int, db: db_dependency):
    return delete_tx(user['id'], tx_id, db)

@router.post("/import-csv", status_code=status.HTTP_200_OK, response_model=ImportcsvResponse)
async def import_csv_endpoint(user: user_dependency, db: db_dependency, account_id: int = Form(...), file: UploadFile = File(...),):
    return import_csv(user['id'], account_id, file, db)

@router.post("/classify-pending", status_code=status.HTTP_200_OK, response_model=ClassifyPendingResponse)
async def classify_pending_transactions_endpoint(user: user_dependency,db: db_dependency):
    return classify_all_transactions(user['id'], db)