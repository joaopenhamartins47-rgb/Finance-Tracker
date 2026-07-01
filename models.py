#Aqui vao ficar as tabelas do banco de dados
from database import Base
from sqlalchemy import Column, Integer,String, Boolean, ForeignKey, Enum as SAEnum, Numeric, Date, DateTime
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

#accounts - origem do dinheiro (cartão vs conta corrente)

class AccountType(PyEnum):
    CREDIT_CARD = "credit_card"
    CHECKING = "checking"

class Accounts(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    account_type = Column(SAEnum(AccountType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)

class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric, nullable=False)
    description = Column(String)
    transaction_date = Column(Date, nullable=False)
    raw_import_hash = Column(String, index=True, unique=True)
    is_classified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
