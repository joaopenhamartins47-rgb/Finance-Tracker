from pydantic import BaseModel, ConfigDict, EmailStr, Field
from models import AccountType
from datetime import date
from decimal import Decimal
from models import AccountType


# Esquema de Entrada (Input)
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)

# Esquema de Saída (Output)
class UserResponse(BaseModel):
    id: int
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None)

class UserUpdatePassword(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class CreateAccountRequest(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    account_type: AccountType

class UpdateAccountRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=30)
    account_type: AccountType | None = Field(default=None)


class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str = Field(min_length=3, max_length=30)
    account_type: AccountType

    model_config = ConfigDict(from_attributes=True)


class CategoriesResponse(BaseModel):
    id: int
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class CreateUpdateCategory(BaseModel):
    name: str

class CreateTransactionRequest(BaseModel):
    account_id: int
    category_id: int
    amount: Decimal
    description: str | None = None
    transaction_date: date


class UpdateTransactionRequest(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    amount: Decimal | None = None
    description: str | None = None
    transaction_date: date | None = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    category_id: int
    amount: Decimal
    description: str | None
    transaction_date: date
    is_classified: bool
    category: CategoriesResponse | None
    account: AccountResponse

    model_config = ConfigDict(from_attributes=True)

class ImportcsvResponse(BaseModel):
    importadas: int
    duplicadas: int



