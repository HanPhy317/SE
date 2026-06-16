"""API routes - authentication (login, register, profile)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database import get_db
from managers.user_manager import UserManager
from config import ADMIN_PASSWORD
from models.rider import Rider
from utils.jwt_util import create_token
from utils.api import ok, fail
from utils.auth_dep import get_current_user

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------- Request Models ----------
class RegisterReq(BaseModel):
    username: str
    phone: str
    password: str

class LoginReq(BaseModel):
    account: str
    password: str
    role: str = "user"

class BecomeRiderReq(BaseModel):
    service_area: str


class UpdateProfileReq(BaseModel):
    phone: str | None = None
    default_address: str | None = None


class TopupReq(BaseModel):
    amount: float


# ---------- Auth Endpoints ----------
@auth_router.post("/register")
async def register(req: RegisterReq, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    success, message, user = await UserManager.register(
        db, username=req.username, phone=req.phone, password=req.password
    )
    if not success:
        return fail(message, code=400)

    token = create_token(user.user_id, user.username, "user")
    return ok({
        "token": token,
        "user_id": user.user_id,
        "username": user.username,
        "role": "user",
        "balance": float(user.balance),
    }, message=message)


@auth_router.post("/login")
async def login(req: LoginReq, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # Admin login bypass (hardcoded account, not in database)
    if req.account == "admin":
        if req.password != ADMIN_PASSWORD:
            return fail("管理员密码错误", code=401)
        token = create_token(user_id=0, username="admin", role="admin")
        return ok({
            "token": token,
            "user_id": 0,
            "username": "admin",
            "role": "admin",
        }, message="管理员登录成功")

    success, message, user = await UserManager.login(
        db, account=req.account, password=req.password
    )
    if not success:
        return fail(message, code=401)

    role = req.role
    rider_id = None
    if role == "rider":
        result = await db.execute(
            select(Rider).where(Rider.user_id == user.user_id)
        )
        rider = result.scalar_one_or_none()
        if rider:
            rider_id = rider.rider_id

    token = create_token(user.user_id, user.username, role)
    return ok({
        "token": token,
        "user_id": user.user_id,
        "username": user.username,
        "role": role,
        "rider_id": rider_id,
        "balance": float(user.balance),
    }, message="登录成功")


@auth_router.get("/profile")
async def get_profile(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户个人信息"""
    success, msg, user_obj, rider = await UserManager.get_profile(
        db, user["user_id"]
    )
    if not success:
        return fail(msg)

    data = {
        "user_id": user_obj.user_id,
        "username": user_obj.username,
        "phone": user_obj.phone,
        "balance": float(user_obj.balance),
        "default_address": user_obj.default_address,
        "created_at": user_obj.created_at.isoformat() if user_obj.created_at else None,
    }
    if rider:
        data["rider"] = {
            "rider_id": rider.rider_id,
            "credit_score": round(float(rider.credit_score or 5.0), 1),
            "total_orders": rider.total_orders,
            "praise_rate": round(float(rider.praise_rate or 1.0), 2),
            "service_area": rider.service_area,
            "rider_status": rider.rider_status,
            "created_at": rider.created_at.isoformat() if rider.created_at else None,
        }
    return ok(data)


@auth_router.post("/become_rider")
async def become_rider(
    req: BecomeRiderReq,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """注册成为骑手"""
    success, msg, rider_obj = await UserManager.become_rider(
        db, user["user_id"], req.service_area
    )
    if not success:
        return fail(msg)

    return ok({
        "rider_id": rider_obj.rider_id,
        "service_area": rider_obj.service_area,
    }, message="注册骑手成功")


@auth_router.put("/profile")
async def update_profile(
    req: UpdateProfileReq,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改个人信息（手机号、默认地址）"""
    success, msg, user_obj = await UserManager.update_profile(
        db, user["user_id"],
        phone=req.phone,
        default_address=req.default_address,
    )
    if not success:
        return fail(msg)

    return ok({
        "user_id": user_obj.user_id,
        "username": user_obj.username,
        "phone": user_obj.phone,
        "default_address": user_obj.default_address,
        "balance": float(user_obj.balance),
    }, message=msg)


@auth_router.post("/topup")
async def topup(
    req: TopupReq,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """账户充值"""
    success, msg, new_balance = await UserManager.topup(
        db, user["user_id"], req.amount
    )
    if not success:
        return fail(msg)

    return ok({
        "balance": round(new_balance, 2),
    }, message=msg)
