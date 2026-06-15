"""Rider model - riders table"""

from datetime import datetime
from sqlalchemy import String, DateTime, Float, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Rider(Base):
    __tablename__ = "riders"

    rider_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), unique=True, nullable=False
    )
    credit_score: Mapped[float | None] = mapped_column(
        Float(1), default=5.0
    )
    total_orders: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    praise_rate: Mapped[float | None] = mapped_column(
        Float(1), default=1.00
    )
    service_area: Mapped[str | None] = mapped_column(String(128), default=None)
    rider_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="offline"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="rider")
    accepted_orders = relationship(
        "Order", back_populates="rider", foreign_keys="Order.rider_id"
    )
