from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum, Numeric, Date, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    accounts = relationship("Accounts", back_populates="user")
    categories = relationship("Categories", back_populates="user")
    transactions = relationship("Transactions", back_populates="user")


# accounts - origem do dinheiro (cartão vs conta corrente)

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

    user = relationship("Users", back_populates="accounts")
    transactions = relationship("Transactions", back_populates="account")


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    exclude_from_reports = Column(Boolean, default=False)

    user = relationship("Users", back_populates="categories")
    transactions = relationship("Transactions", back_populates="category")


class Transactions(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        UniqueConstraint("user_id", "raw_import_hash", name="uq_transaction_user_hash"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String)
    transaction_date = Column(Date, nullable=False)
    raw_import_hash = Column(String, index=True)
    is_classified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="transactions")
    account = relationship("Accounts", back_populates="transactions")
    category = relationship("Categories", back_populates="transactions")