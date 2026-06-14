"""Balance top-up and deduction service."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.user import User
from app.models.balance import BalanceTransaction, TransactionType
from app.core.config import settings


async def top_up_balance(
    user: User,
    amount_rwf: float,
    payment_reference: str,
    db: AsyncSession,
) -> float:
    if amount_rwf < settings.MIN_TOPUP_RWF:
        raise ValueError(f"Minimum top-up is {settings.MIN_TOPUP_RWF} RWF")

    new_balance = user.balance_rwf + amount_rwf
    await db.execute(
        update(User).where(User.id == user.id).values(balance_rwf=new_balance)
    )
    tx = BalanceTransaction(
        user_id=user.id,
        type=TransactionType.TOPUP,
        amount_rwf=amount_rwf,
        balance_after=new_balance,
        reference_id=payment_reference,
        description=f"Top-up: {amount_rwf:.0f} RWF",
    )
    db.add(tx)
    await db.flush()
    return new_balance
