"""ReviewManager - review creation, rating recalculation, and query logic."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Review
from models.order import Order, ORDER_STATUS_COMPLETED
from models.rider import Rider


class ReviewManager:
    """Business logic for order reviews and rider rating management."""

    @staticmethod
    async def create_review(
        db: AsyncSession,
        order_id: int,
        reviewer_id: int,
        rating: float,
        comment: str | None = None,
    ) -> tuple[bool, str, Review | None]:
        """Create a review for a completed order. Only the publisher can review."""

        result = await db.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return False, "订单不存在", None

        if order.status != ORDER_STATUS_COMPLETED:
            return False, "只能评价已完成的订单", None

        if order.publisher_id != reviewer_id:
            return False, "只能评价自己发布的订单", None

        if not order.rider_id:
            return False, "该订单没有骑手，无法评价", None

        existing = await db.execute(
            select(Review).where(Review.order_id == order_id)
        )
        if existing.scalar_one_or_none():
            return False, "该订单已评价过", None

        # Get reviewee (rider's user_id)
        result = await db.execute(
            select(Rider).where(Rider.rider_id == order.rider_id)
        )
        rider = result.scalar_one_or_none()
        if not rider:
            return False, "骑手不存在", None

        review = Review(
            order_id=order_id,
            reviewer_id=reviewer_id,
            reviewee_id=rider.user_id,
            rating=rating,
            comment=comment,
        )
        db.add(review)
        await db.flush()

        await ReviewManager._recalculate_rider_stats(db, order.rider_id)

        await db.commit()
        await db.refresh(review)
        return True, "评价成功", review

    @staticmethod
    async def _recalculate_rider_stats(db: AsyncSession, rider_id: int):
        """Recalculate credit_score and praise_rate for a rider based on all their reviews."""
        result = await db.execute(
            select(Rider).where(Rider.rider_id == rider_id)
        )
        rider = result.scalar_one_or_none()
        if not rider:
            return

        result = await db.execute(
            select(
                func.count(Review.review_id),
                func.avg(Review.rating),
                func.sum(
                    func.if_(Review.rating >= 4, 1, 0)
                ),
            ).where(Review.reviewee_id == rider.user_id)
        )
        total, avg_rating, praise_count = result.one()

        rider.credit_score = round(float(avg_rating), 1) if avg_rating else 5.0
        rider.praise_rate = round(float(praise_count or 0) / float(total), 2) if total else 1.00

    @staticmethod
    async def get_review_by_order(db: AsyncSession, order_id: int) -> Review | None:
        """Get the review for a specific order, if any."""
        result = await db.execute(
            select(Review).where(Review.order_id == order_id)
        )
        return result.scalar_one_or_none()
