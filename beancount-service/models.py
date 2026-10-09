"""
Pydantic models for request/response validation
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class AccountType(str, Enum):
    """Account type enumeration"""

    ASSETS = "Assets"
    LIABILITIES = "Liabilities"
    EQUITY = "Equity"
    INCOME = "Income"
    EXPENSES = "Expenses"


class Account(BaseModel):
    """Account model"""

    name: str
    type: AccountType
    display_name: Optional[str] = None


class Payee(BaseModel):
    """Payee model"""

    name: str


class TransactionPosting(BaseModel):
    """Transaction posting (line item)"""

    account: str
    amount: float
    currency: Optional[str] = "EUR"
    comment: Optional[str] = None


class Transaction(BaseModel):
    """Complete transaction"""

    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    payee: str
    narration: str
    postings: List[TransactionPosting]
    tags: Optional[List[str]] = None
    links: Optional[List[str]] = None
    metadata: Optional[Dict[str, str]] = None


class ReceiptTransactionItem(BaseModel):
    """Receipt transaction item"""

    name: str
    price: float
    expense_account: Optional[str] = None


class ReceiptTransactionData(BaseModel):
    """Receipt transaction data for convenience endpoint"""

    receipt_id: int
    description: Optional[str] = None
    payee: str
    source_account: str
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    items: List[ReceiptTransactionItem]
    total: float
    currency: Optional[str] = "EUR"


class TransactionSubmitResponse(BaseModel):
    """Response from transaction submission"""

    success: bool
    message: Optional[str] = None
    transaction_id: Optional[str] = None


class AccountsResponse(BaseModel):
    """Response containing list of accounts"""

    accounts: List[Account]


class PayeesResponse(BaseModel):
    """Response containing list of payees"""

    payees: List[Payee]


class MonthlyExpensesResponse(BaseModel):
    """Response containing monthly expenses by currency"""

    expenses_by_currency: Dict[str, float]
    year: int
    month: int
