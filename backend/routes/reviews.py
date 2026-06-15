"""API routes - order reviews."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from database import get_db
from managers.review_manager import ReviewManager
from utils.api import ok, fail
from utils.auth_dep import get_current_user

review_router = APIRouter(prefix="/api/reviews", tags=["reviews"])


class CreateReviewReq(BaseModel):
    order_id: int
    rating: float = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=512)


@review_router.post("/create")
async def create_review(
    req: CreateReviewReq,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a review for a completed order."""
    success, msg, review = await ReviewManager.create_review(
        db,
        order_id=req.order_id,
        reviewer_id=user["user_id"],
        rating=req.rating,
        comment=req.comment,
    )
    if not success:
        return fail(msg)

    return ok({
        "review_id": review.review_id,
        "order_id": review.order_id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }, message=msg)


@review_router.get("/order/{order_id}")
async def get_order_review(
    order_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if an order has been reviewed and get the review."""
    review = await ReviewManager.get_review_by_order(db, order_id)
    if not review:
        return ok({"reviewed": False, "review": None})

    return ok({
        "reviewed": True,
        "review": {
            "review_id": review.review_id,
            "order_id": review.order_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        },
    })
