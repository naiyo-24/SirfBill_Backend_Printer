from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from models.database import get_db
from models.transaction import Transaction
from models.account import Account
from models.enums import TransactionType, AccountType

router = APIRouter(
    prefix="/api/accounts/extended",
    tags=["Extended Accounting"]
)

@router.get("/receivables")
def get_receivables(db: Session = Depends(get_db)):
    # Receivables: transactions where entity_type == 'CUSTOMER' and status == 'UNPAID' or 'PARTIAL'
    # Actually, simpler: just return all customers and their outstanding balance based on transactions.
    # Group by entity_name.
    
    results = (
        db.query(
            Transaction.entity_name,
            func.sum(Transaction.amount).label("total_owed")
        )
        .filter(Transaction.entity_type == 'CUSTOMER')
        .filter(Transaction.status.in_(['UNPAID', 'PARTIAL']))
        .group_by(Transaction.entity_name)
        .all()
    )
    
    data = []
    total_receivables = 0.0
    for row in results:
        data.append({
            "entity_name": row.entity_name,
            "amount_owed": row.total_owed
        })
        total_receivables += row.total_owed
        
    return {
        "status": "success",
        "data": {
            "receivables": data,
            "total_receivables": total_receivables
        }
    }

@router.get("/payables")
def get_payables(db: Session = Depends(get_db)):
    # Payables: transactions where entity_type == 'SUPPLIER' and status in UNPAID/PARTIAL
    results = (
        db.query(
            Transaction.entity_name,
            func.sum(Transaction.amount).label("total_owed")
        )
        .filter(Transaction.entity_type == 'SUPPLIER')
        .filter(Transaction.status.in_(['UNPAID', 'PARTIAL']))
        .group_by(Transaction.entity_name)
        .all()
    )
    
    data = []
    total_payables = 0.0
    for row in results:
        data.append({
            "entity_name": row.entity_name,
            "amount_owed": row.total_owed
        })
        total_payables += row.total_owed
        
    return {
        "status": "success",
        "data": {
            "payables": data,
            "total_payables": total_payables
        }
    }

@router.get("/ledger")
def get_ledger(db: Session = Depends(get_db)):
    # Returns all accounts and their current balances
    accounts = db.query(Account).all()
    data = []
    for acc in accounts:
        data.append({
            "id": str(acc.id),
            "name": acc.name,
            "type": acc.account_type.value,
            "balance": acc.balance
        })
        
    return {
        "status": "success",
        "data": data
    }

@router.get("/reports/pnl")
def get_pnl(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.date <= datetime.fromisoformat(end_date))
        
    income = query.filter(Transaction.transaction_type == TransactionType.INCOME).with_entities(func.sum(Transaction.amount)).scalar() or 0.0
    expense = query.filter(Transaction.transaction_type == TransactionType.EXPENSE).with_entities(func.sum(Transaction.amount)).scalar() or 0.0
    
    return {
        "status": "success",
        "data": {
            "total_income": income,
            "total_expense": expense,
            "net_profit": income - expense
        }
    }
