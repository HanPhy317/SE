"""UserManager - user registration, login, profile, rider registration, balance management"""

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.rider import Rider


class UserManager:
    """Business logic for user account operations."""

    @staticmethod
    async def register(
        db: AsyncSession,
        username: str,
        phone: str,
        password: str
    ) -> tuple[bool, str, User | None]:
        """Register a new user. Returns (success, message, user)."""
        # Check username uniqueness
        result = await db.execute(
            select(User).where(User.username == username)
        )
        if result.scalar_one_or_none():
            return False, "用户名已被注册", None

        # Check phone uniqueness
        result = await db.execute(
            select(User).where(User.phone == phone)
        )
        if result.scalar_one_or_none():
            return False, "手机号已被注册", None

        # Create user
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        user = User(
            username=username,
            phone=phone,
            password_hash=password_hash,
            balance=100.00  # Initial balance for testing
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return True, "注册成功", user

    @staticmethod
    async def login(
        db: AsyncSession,
        account: str,
        password: str
    ) -> tuple[bool, str, User | None]:
        """Authenticate user by username or phone. Returns (success, message, user)."""
        # Try username first
        result = await db.execute(
            select(User).where(User.username == account)
        )
        user = result.scalar_one_or_none()

        # Try phone if username not found
        if not user:
            result = await db.execute(
                select(User).where(User.phone == account)
            )
            user = result.scalar_one_or_none()

        if not user:
            return False, "账号不存在", None

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8")
        ):
            return False, "密码错误", None

        return True, "登录成功", user

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: int
    ) -> tuple[bool, str, User | None, Rider | None]:
        """Get user profile and rider info. Returns (success, message, user, rider)."""
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False, "用户不存在", None, None

        result = await db.execute(
            select(Rider).where(Rider.user_id == user_id)
        )
        rider = result.scalar_one_or_none()
        return True, "查询成功", user, rider

    @staticmethod
    async def become_rider(
        db: AsyncSession,
        user_id: int,
        service_area: str
    ) -> tuple[bool, str, Rider | None]:
        """Register current user as a rider. Returns (success, message, rider)."""
        # Check if already a rider
        result = await db.execute(
            select(Rider).where(Rider.user_id == user_id)
        )
        existing_rider = result.scalar_one_or_none()
        if existing_rider:
            return False, "您已经是骑手了", existing_rider

        rider = Rider(
            user_id=user_id,
            service_area=service_area,
            rider_status="offline",
            total_orders=0,
            praise_rate=1.00,
            credit_score=5.0
        )
        db.add(rider)
        await db.commit()
        await db.refresh(rider)
        return True, "骑手注册成功", rider

    @staticmethod
    async def update_balance(
        db: AsyncSession,
        user_id: int,
        amount: float
    ) -> tuple[bool, str]:
        """Update user balance by amount (positive = add, negative = deduct)."""
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False, "用户不存在"

        new_balance = float(user.balance) + amount
        if new_balance < 0:
            return False, "余额不足"

        user.balance = new_balance
        await db.commit()
        return True, "余额更新成功"

    @staticmethod
    async def get_rider_info(
        db: AsyncSession,
        rider_id: int
    ) -> tuple[bool, str, Rider | None]:
        """Get rider information."""
        result = await db.execute(
            select(Rider).where(Rider.rider_id == rider_id)
        )
        rider = result.scalar_one_or_none()
        if not rider:
            return False, "骑手不存在", None
        return True, "查询成功", rider
