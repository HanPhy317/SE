"""Review model - reviews table for order reviews"""

from datetime import datetime
from sqlalchemy import String, DateTime, Float, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.order_id"), unique=True, nullable=False
    )
    reviewer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )
    reviewee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )
    rating: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    comment: Mapped[str | None] = mapped_column(
        String(512), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
