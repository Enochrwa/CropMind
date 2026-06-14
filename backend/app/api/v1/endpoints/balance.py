from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.balance import BalanceTransaction
from app.schemas.balance import TopUpRequest, BalanceOut, TransactionOut
from app.services.balance_service import top_up_balance

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get("/", response_model=BalanceOut)
async def get_balance(current_user: User = Depends(get_current_user)):
    return BalanceOut(balance_rwf=current_user.balance_rwf, user_id=current_user.id)


@router.post("/topup", response_model=BalanceOut)
async def topup(
    payload: TopUpRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        new_balance = await top_up_balance(
            current_user, payload.amount_rwf, payload.payment_reference or "", db
        )
        return BalanceOut(balance_rwf=new_balance, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=List[TransactionOut])
async def transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
):
    result = await db.execute(
        select(BalanceTransaction)
        .where(BalanceTransaction.user_id == current_user.id)
        .order_by(BalanceTransaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()
