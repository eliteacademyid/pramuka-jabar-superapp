from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_item = (
        db.query(models.OrderItem)
        .join(models.Order, models.OrderItem.order_id == models.Order.id)
        .filter(models.OrderItem.id == payload.order_item_id)
        .first()
    )
    if not order_item or order_item.order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item order tidak ditemukan"
        )
    if order_item.order.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order belum selesai"
        )
    existing = (
        db.query(models.Review)
        .filter(models.Review.order_item_id == payload.order_item_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item sudah diulas"
        )

    review = models.Review(
        order_item_id=payload.order_item_id,
        user_id=current_user.id,
        product_id=order_item.product_id,
        rating=payload.rating,
        comment=payload.comment,
        status="visible",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return schemas.ReviewOut(
        id=review.id,
        order_item_id=review.order_item_id,
        user_id=review.user_id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
        status=review.status,
        created_at=review.created_at,
        username=current_user.username,
    )
