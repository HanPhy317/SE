"""API routes - user order operations."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database import get_db
from managers.order_manager import OrderManager
from managers.user_manager import UserManager
from utils.api import ok, fail
from utils.auth_dep import get_current_user

order_router = APIRouter(prefix="/api/orders", tags=["orders"])


class CreateOrderReq(BaseModel):
    order_type: str
    reward: float
    delivery_addr: str
    biz_fields: dict = {}


class CancelOrderReq(BaseModel):
    order_id: int


@order_router.get("/my")
async def my_orders(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的所有订单"""
    from managers.order_manager import OrderManager as OM
    orders = await OM.get_orders_by_user(db, user["user_id"])

    def serialize(o):
        return {
            "order_id": o.order_id,
            "order_no": o.order_no,
            "order_type": o.order_type,
            "status": o.status,
            "reward": float(o.reward),
            "delivery_addr": o.delivery_addr,
            "biz_fields": o.get_biz_fields(),
            "rider_id": o.rider_id,
            "publisher_id": o.publisher_id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "completed_at": o.completed_at.isoformat() if o.completed_at else None,
        }

    pending = [serialize(o) for o in orders if o.status == "pending"]
    active = [serialize(o) for o in orders if o.status in ("accepted", "delivering")]
    delivered = [serialize(o) for o in orders if o.status == "delivered"]
    completed = [serialize(o) for o in orders if o.status == "completed"]
    cancelled = [serialize(o) for o in orders if o.status == "cancelled"]

    # Attach review data for completed orders
    from models.review import Review
    from sqlalchemy import select as sa_select
    completed_ids = [c["order_id"] for c in completed]
    if completed_ids:
        result = await db.execute(
            sa_select(Review).where(Review.order_id.in_(completed_ids))
        )
        reviews = {r.order_id: r for r in result.scalars().all()}
        for c in completed:
            r = reviews.get(c["order_id"])
            c["review"] = {
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            } if r else None

    return ok({
        "pending": pending,
        "active": active,
        "delivered": delivered,
        "completed": completed,
        "cancelled": cancelled,
    })


@order_router.get("/pending")
async def pending_orders(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """骑手获取所有待接单订单"""
    orders = await OrderManager.get_pending(db)

    def serialize(o):
        return {
            "order_id": o.order_id,
            "order_no": o.order_no,
            "order_type": o.order_type,
            "status": o.status,
            "reward": float(o.reward),
            "delivery_addr": o.delivery_addr,
            "biz_fields": o.get_biz_fields(),
            "publisher_id": o.publisher_id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }

    return ok([serialize(o) for o in orders])


@order_router.get("/rider/my")
async def rider_orders(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """骑手获取自己的订单"""
    from models.rider import Rider
    from sqlalchemy import select
    result = await db.execute(
        select(Rider).where(Rider.user_id == user["user_id"])
    )
    rider = result.scalar_one_or_none()
    if not rider:
        return fail("你不是骑手")

    orders = await OrderManager.get_orders_by_rider(db, rider.rider_id)

    def serialize(o):
        return {
            "order_id": o.order_id,
            "order_no": o.order_no,
            "order_type": o.order_type,
            "status": o.status,
            "reward": float(o.reward),
            "delivery_addr": o.delivery_addr,
            "biz_fields": o.get_biz_fields(),
            "publisher_id": o.publisher_id,
            "rider_id": o.rider_id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "completed_at": o.completed_at.isoformat() if o.completed_at else None,
        }

    active = [serialize(o) for o in orders if o.status in ("accepted", "delivering", "delivered")]
    completed = [serialize(o) for o in orders if o.status == "completed"]

    # Attach review data for completed orders
    from models.review import Review
    completed_ids = [c["order_id"] for c in completed]
    if completed_ids:
        result_r = await db.execute(
            select(Review).where(Review.order_id.in_(completed_ids))
        )
        reviews = {r.order_id: r for r in result_r.scalars().all()}
        for c in completed:
            r = reviews.get(c["order_id"])
            c["review"] = {
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            } if r else None

    return ok({"active": active, "completed": completed})


@order_router.get("/{order_id}")
async def order_detail(
    order_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个订单详情"""
    order = await OrderManager.get_order_by_id(db, order_id)
    if not order:
        return fail("订单不存在")

    return ok({
        "order_id": order.order_id,
        "order_no": order.order_no,
        "order_type": order.order_type,
        "status": order.status,
        "reward": float(order.reward),
        "delivery_addr": order.delivery_addr,
        "biz_fields": order.get_biz_fields(),
        "publisher_id": order.publisher_id,
        "rider_id": order.rider_id,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
    })


@order_router.post("/create")
async def create_order(
    req: CreateOrderReq,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发布新订单"""
    success, message, order = await OrderManager.create(
        db,
        publisher_id=user["user_id"],
        order_type=req.order_type,
        biz_fields=req.biz_fields,
        reward=req.reward,
        delivery_addr=req.delivery_addr,
    )
    if not success:
        return fail(message)

    return ok({
        "order_id": order.order_id,
        "order_no": order.order_no,
    }, message=message)


@order_router.post("/accept/{order_id}")
async def accept_order(
    order_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """骑手接单"""
    from models.rider import Rider
    from sqlalchemy import select
    result = await db.execute(
        select(Rider).where(Rider.user_id == user["user_id"])
    )
    rider = result.scalar_one_or_none()
    if not rider:
        return fail("你不是骑手，请先注册骑手")

    success, msg = await OrderManager.accept(db, order_id, rider.rider_id)
    if not success:
        return fail(msg)

    return ok(None, message="接单成功")


@order_router.post("/update_status")
async def update_status(
    order_id: int,
    status: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新订单配送状态: delivering / delivered"""
    success, msg = await OrderManager.update_status(db, order_id, status)
    if not success:
        return fail(msg)
    return ok(None, message="状态更新成功")


@order_router.post("/cancel/{order_id}")
async def cancel_order(
    order_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消订单（仅待接单状态可取消）"""
    success, msg = await OrderManager.cancel(db, order_id)
    if not success:
        return fail(msg)
    return ok(None, message="订单已取消")


@order_router.post("/complete/{order_id}")
async def complete_order(
    order_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """确认收货并结算"""
    success, msg = await OrderManager.complete(db, order_id)
    if not success:
        return fail(msg)
    return ok(None, message="结算完成")
