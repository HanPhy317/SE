"""API routes - admin operations (users list, transactions, ban/unban)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from models.transaction import Transaction
from models.order import Order
from utils.api import ok, fail
from utils.auth_dep import require_admin

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@admin_router.get("/users")
async def list_users(
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取所有用户列表"""
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return ok([
        {
            "user_id": u.user_id,
            "username": u.username,
            "phone": u.phone,
            "balance": float(u.balance),
            "is_banned": u.is_banned,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ])


@admin_router.get("/transactions")
async def list_transactions(
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取所有交易记录"""
    result = await db.execute(
        select(Transaction).order_by(Transaction.created_at.desc())
    )
    txns = result.scalars().all()

    data = []
    for t in txns:
        user_result = await db.execute(
            select(User.username).where(User.user_id == t.user_id)
        )
        username = user_result.scalar_one_or_none()

        order_result = await db.execute(
            select(Order.order_no).where(Order.order_id == t.order_id)
        )
        order_no = order_result.scalar_one_or_none()

        data.append({
            "txn_id": t.txn_id,
            "user_id": t.user_id,
            "username": username or "已删除",
            "order_id": t.order_id,
            "order_no": order_no or "已删除",
            "amount": float(t.amount),
            "txn_type": t.txn_type,
            "description": t.description,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })

    return ok(data)


@admin_router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """封禁用户"""
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return fail("用户不存在")
    if user.is_banned:
        return fail("该用户已被封禁")

    user.is_banned = True
    await db.commit()
    return ok(None, message="用户已封禁")


@admin_router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """解封用户"""
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return fail("用户不存在")
    if not user.is_banned:
        return fail("该用户未被封禁")

    user.is_banned = False
    await db.commit()
    return ok(None, message="用户已解封")
