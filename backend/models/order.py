"""Order model - orders table"""

import json
from datetime import datetime
from sqlalchemy import (
    String, DateTime, Numeric, BigInteger, ForeignKey, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# Order status values
ORDER_STATUS_PENDING = "pending"       # 待接单
ORDER_STATUS_ACCEPTED = "accepted"     # 已接单
ORDER_STATUS_DELIVERING = "delivering"  # 配送中
ORDER_STATUS_DELIVERED = "delivered"   # 已送达
ORDER_STATUS_COMPLETED = "completed"   # 已完成
ORDER_STATUS_CANCELLED = "cancelled"   # 已取消

# Order type values
ORDER_TYPE_TAKEOUT = "takeout"      # 外卖跑腿
ORDER_TYPE_EXPRESS = "express"      # 快递跑腿
ORDER_TYPE_SHOPPING = "shopping"    # 代买服务
ORDER_TYPE_CUSTOM = "custom"        # 自定义跑腿


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    order_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False
    )
    order_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    publisher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False
    )
    rider_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("riders.rider_id"), default=None
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ORDER_STATUS_PENDING
    )
    reward: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    delivery_sub_status: Mapped[str | None] = mapped_column(
        String(20), default=None
    )
    delivery_addr: Mapped[str] = mapped_column(
        String(256), nullable=False
    )
    biz_fields: Mapped[str] = mapped_column(
        Text, nullable=False, default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=None
    )

    # Relationships
    publisher = relationship(
        "User", back_populates="published_orders", foreign_keys=[publisher_id]
    )
    rider = relationship(
        "Rider", back_populates="accepted_orders", foreign_keys=[rider_id]
    )

    def get_biz_fields(self) -> dict:
        """Parse biz_fields JSON string to dict."""
        return json.loads(self.biz_fields) if self.biz_fields else {}

    def set_biz_fields(self, data: dict):
        """Set biz_fields from dict to JSON string."""
        self.biz_fields = json.dumps(data, ensure_ascii=False)
