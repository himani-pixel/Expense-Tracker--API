
from pydantic import BaseModel, ConfigDict, Field


# Create Budget
class BudgetCreate(BaseModel):
    category_id: int = Field(gt=0)
    amount: float = Field(gt=0, le=10000000)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020, le=2100)


# Budget Response
class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: float
    month: int
    year: int

    model_config = ConfigDict(from_attributes=True)
