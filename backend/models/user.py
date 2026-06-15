"""User model - users table"""

from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0.00
    )
    default_address: Mapped[str | None] = mapped_column(String(256), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    rider = relationship("Rider", back_populates="user", uselist=False)
    published_orders = relationship(
        "Order", back_populates="publisher", foreign_keys="Order.publisher_id"
    )
