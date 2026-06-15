"""Transaction model - transactions table for balance records"""

from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    txn_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.order_id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    txn_type: Mapped[str] = mapped_column(
        String(20), nullable=False  # "debit" / "credit" / "refund"
    )
    description: Mapped[str | None] = mapped_column(
        String(256), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
