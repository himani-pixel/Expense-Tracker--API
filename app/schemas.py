
from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from decimal import Decimal
from typing import Optional


# Create Expense
class ExpenseCreate(BaseModel):
    category_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=150)
    amount: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500
    )
    expense_date: date


# Expense Response
class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    title: str
    amount: Decimal
    description: Optional[str] = None
    expense_date: date

    model_config = ConfigDict(from_attributes=True)
