from sqlalchemy import func
from datetime import date
import calendar
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Budget
from app.budget_schemas import BudgetCreate, BudgetResponse
from datetime import date

from app.database import get_db
from app.models import User, Expense
from app.schemas import ExpenseCreate, ExpenseResponse
from app.user_schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

app = FastAPI(title="Expense Tracker API")


@app.get("/")
def home():
    return {"message": "Welcome to Expense Tracker API"}


# REGISTER
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# LOGIN
@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user or not verify_password(
        user.password, existing_user.password
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(existing_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ADD EXPENSE
@app.post("/expenses", response_model=ExpenseResponse)
def add_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_expense = Expense(
        **expense.model_dump(),
        user_id=current_user.id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


# VIEW USER EXPENSES
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Expense).filter(
        Expense.user_id == current_user.id
    ).all()


# UPDATE EXPENSE
@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    updated_expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in updated_expense.model_dump().items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)

    return expense


# DELETE EXPENSE
@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}


# CATEGORY-WISE EXPENSE REPORT
@app.get("/reports/category")
def category_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models import Category

    report = (
        db.query(
            Category.name.label("category"),
            func.sum(Expense.amount).label("total_amount")
        )
        .join(Category, Expense.category_id == Category.id)
        .filter(Expense.user_id == current_user.id)
        .group_by(Category.name)
        .all()
    )

    return [
        {
            "category": item.category,
            "total_amount": float(item.total_amount)
        }
        for item in report
    ]


# MONTHLY EXPENSE SUMMARY
@app.get("/reports/monthly")
def monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid month")

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    result = db.query(
        func.sum(Expense.amount),
        func.count(Expense.id)
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).first()

    return {
        "year": year,
        "month": month,
        "total_expenses": float(result[0] or 0),
        "total_transactions": result[1]
    }


# TOTAL EXPENSE SUMMARY
@app.get("/reports/total")
def total_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        func.sum(Expense.amount),
        func.count(Expense.id)
    ).filter(
        Expense.user_id == current_user.id
    ).first()

    return {
        "total_spending": float(result[0] or 0),
        "total_transactions": result[1]
    }

# CREATE BUDGET
@app.post("/budgets", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget.category_id,
        Budget.month == budget.month,
        Budget.year == budget.year
    ).first()

    if existing_budget:
        raise HTTPException(
            status_code=400,
            detail="Budget already exists for this category and month"
        )

    new_budget = Budget(
        **budget.model_dump(),
        user_id=current_user.id
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


# VIEW ALL BUDGETS
@app.get("/budgets", response_model=list[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Budget).filter(
        Budget.user_id == current_user.id
    ).all()


# CHECK BUDGET STATUS
@app.get("/budgets/{budget_id}/status")
def budget_status(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    total_spent = db.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user.id,
        Expense.category_id == budget.category_id,
        Expense.expense_date >= date(budget.year, budget.month, 1),
        Expense.expense_date <= date(
            budget.year,
            budget.month,
            calendar.monthrange(budget.year, budget.month)[1]
        )
    ).scalar() or 0

    remaining = float(budget.amount) - float(total_spent)

    return {
        "budget_id": budget.id,
        "budget_amount": float(budget.amount),
        "total_spent": float(total_spent),
        "remaining_amount": remaining,
        "status": "Exceeded" if remaining < 0 else "Within Budget"
    }
