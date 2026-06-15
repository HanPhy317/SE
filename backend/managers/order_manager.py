"""OrderManager - order creation, acceptance, status management, and settlement"""

import json
import uuid
import asyncio
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import (
    Order,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_ACCEPTED,
    ORDER_STATUS_DELIVERING,
    ORDER_STATUS_DELIVERED,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_CANCELLED,
)
from models.transaction import Transaction
from managers.user_manager import UserManager


class OrderManager:
    """Business logic for order lifecycle operations."""

    # Static lock dictionary per order_id for concurrent accept safety
    _accept_locks: dict[int, asyncio.Lock] = {}

    @staticmethod
    def _get_lock(order_id: int) -> asyncio.Lock:
        """Get or create a per-order lock for concurrent accept protection."""
        if order_id not in OrderManager._accept_locks:
            OrderManager._accept_locks[order_id] = asyncio.Lock()
        return OrderManager._accept_locks[order_id]

    @staticmethod
    async def create(
        db: AsyncSession,
        publisher_id: int,
        order_type: str,
        biz_fields: dict,
        reward: float,
        delivery_addr: str
    ) -> tuple[bool, str, Order | None]:
        """Create a new order. Returns (success, message, order)."""
        order_no = f"CE{uuid.uuid4().hex[:12].upper()}"  # CE = Campus Errand

        order = Order(
            order_no=order_no,
            order_type=order_type,
            publisher_id=publisher_id,
            status=ORDER_STATUS_PENDING,
            reward=reward,
            delivery_addr=delivery_addr,
            biz_fields=json.dumps(biz_fields, ensure_ascii=False),
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return True, "订单发布成功", order

    @staticmethod
    async def get_pending(
        db: AsyncSession,
        order_type: str | None = None
    ) -> list[Order]:
        """Get all pending (unclaimed) orders, optionally filtered by type."""
        query = select(Order).where(Order.status == ORDER_STATUS_PENDING)
        if order_type:
            query = query.where(Order.order_type == order_type)
        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def accept(
        db: AsyncSession,
        order_id: int,
        rider_id: int
    ) -> tuple[bool, str]:
        """
        Accept an order with concurrent safety.
        Two-layer locking:
        1. asyncio.Lock (application-level, per-order)
        2. SELECT ... FOR UPDATE (database-level row lock)
        Ensures only one rider grabs the order even under high concurrency.
        Returns (success, message).
        """
        lock = OrderManager._get_lock(order_id)

        async with lock:
            # SELECT ... FOR UPDATE locks the row until transaction commits
            result = await db.execute(
                select(Order)
                .where(Order.order_id == order_id)
                .with_for_update()
            )
            order = result.scalar_one_or_none()

            if not order:
                return False, "订单不存在"

            if order.status != ORDER_STATUS_PENDING:
                return False, "订单已被其他骑手接走"

            if order.publisher_id == rider_id:
                return False, "不能接自己发布的订单"

            # Atomically update to accepted
            order.status = ORDER_STATUS_ACCEPTED
            order.rider_id = rider_id
            await db.commit()
            return True, "接单成功"

    @staticmethod
    async def update_status(
        db: AsyncSession,
        order_id: int,
        status: str
    ) -> tuple[bool, str]:
        """Update order delivery status. Returns (success, message)."""
        result = await db.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return False, "订单不存在"

        valid_transitions = {
            ORDER_STATUS_ACCEPTED: [ORDER_STATUS_DELIVERING, ORDER_STATUS_CANCELLED],
            ORDER_STATUS_DELIVERING: [ORDER_STATUS_DELIVERED],
            ORDER_STATUS_DELIVERED: [ORDER_STATUS_COMPLETED],
            ORDER_STATUS_PENDING: [ORDER_STATUS_CANCELLED],
        }

        if status not in valid_transitions.get(order.status, []):
            return False, f"无法从'{order.status}'变更为'{status}'"

        order.status = status
        if status == ORDER_STATUS_COMPLETED:
            order.completed_at = datetime.utcnow()

        await db.commit()
        return True, "状态更新成功"

    @staticmethod
    async def cancel(
        db: AsyncSession,
        order_id: int
    ) -> tuple[bool, str]:
        """Cancel an order (only pending orders can be cancelled)."""
        return await OrderManager.update_status(db, order_id, ORDER_STATUS_CANCELLED)

    @staticmethod
    async def complete(
        db: AsyncSession,
        order_id: int
    ) -> tuple[bool, str]:
        """
        Complete an order with settlement transaction.
        结算事务：校验delivered → 更新completed → 发布者扣款+流水 → 骑手入账+流水
        """
        result = await db.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return False, "订单不存在"

        if order.status != ORDER_STATUS_DELIVERED:
            return False, "订单尚未送达，无法结算"

        # Begin settlement transaction
        order.status = ORDER_STATUS_COMPLETED
        order.completed_at = datetime.utcnow()

        # Deduct from publisher's balance
        from models.user import User
        result = await db.execute(
            select(User).where(User.user_id == order.publisher_id)
        )
        publisher = result.scalar_one_or_none()
        if publisher:
            new_balance = float(publisher.balance) - float(order.reward)
            if new_balance < 0:
                return False, "发布者余额不足，无法结算"
            publisher.balance = new_balance

        publisher_txn = Transaction(
            user_id=order.publisher_id,
            order_id=order.order_id,
            amount=float(order.reward),
            txn_type="debit",
            description=f"订单 {order.order_no} 结算扣款"
        )
        db.add(publisher_txn)

        # Get rider's user_id and credit balance
        from models.rider import Rider
        result = await db.execute(
            select(Rider).where(Rider.rider_id == order.rider_id)
        )
        rider = result.scalar_one_or_none()

        if rider:
            # Credit rider's associated user
            result = await db.execute(
                select(User).where(User.user_id == rider.user_id)
            )
            rider_user = result.scalar_one_or_none()
            if rider_user:
                rider_user.balance = float(rider_user.balance) + float(order.reward)

            rider_txn = Transaction(
                user_id=rider.user_id,
                order_id=order.order_id,
                amount=float(order.reward),
                txn_type="credit",
                description=f"订单 {order.order_no} 收入"
            )
            db.add(rider_txn)

            # Update rider stats
            rider.total_orders += 1

        await db.commit()
        return True, "订单结算完成"

    @staticmethod
    async def get_orders_by_user(
        db: AsyncSession,
        user_id: int,
        status: str | None = None
    ) -> list[Order]:
        """Get orders published by a specific user."""
        query = select(Order).where(Order.publisher_id == user_id)
        if status:
            query = query.where(Order.status == status)
        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_orders_by_rider(
        db: AsyncSession,
        rider_id: int,
        status: str | None = None
    ) -> list[Order]:
        """Get orders accepted by a specific rider."""
        query = select(Order).where(Order.rider_id == rider_id)
        if status:
            query = query.where(Order.status == status)
        query = query.order_by(Order.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_order_by_id(
        db: AsyncSession,
        order_id: int
    ) -> Order | None:
        """Get a single order by ID."""
        result = await db.execute(
            select(Order).where(Order.order_id == order_id)
        )
        return result.scalar_one_or_none()
