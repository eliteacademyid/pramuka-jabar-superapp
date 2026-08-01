from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/conversations", tags=["chat"])


def _is_participant(user: models.User, conv: models.Conversation) -> bool:
    if user.role == "admin":
        return True
    if conv.order:
        order = conv.order
        if order.buyer_id == user.id or order.store.owner_id == user.id:
            return True
    if conv.product and conv.product.store.owner_id == user.id:
        return True
    if conv.buyer_id == user.id:
        return True
    return False


def _get_conv_or_403(
    db: Session, user: models.User, conversation_id: int
) -> models.Conversation:
    conv = db.get(models.Conversation, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Percakapan tidak ditemukan"
        )
    if not _is_participant(user, conv):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    return conv


def _conv_out(db: Session, conv: models.Conversation, user: models.User) -> schemas.ConversationOut:
    order = conv.order
    product = conv.product
    last = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conv.id)
        .order_by(models.Message.created_at.desc())
        .first()
    )
    unread = (
        db.query(models.Message)
        .filter(
            models.Message.conversation_id == conv.id,
            models.Message.sender_id != user.id,
            models.Message.read_at.is_(None),
        )
        .count()
    )
    participants = []
    if order:
        participants = [
            order.store.owner.username,
            order.buyer.username,
            *[u.username for u in db.query(models.User).filter(models.User.role == "admin").all()],
        ]
    elif product:
        participants = [product.store.owner.username, conv.buyer.username]
    return schemas.ConversationOut(
        id=conv.id,
        order_code=order.order_code if order else None,
        order_status=order.status if order else None,
        product_name=product.name if product else None,
        product_slug=product.slug if product else None,
        store_name=(order.store.name if order else (product.store.name if product else None)),
        store_slug=(order.store.slug if order else (product.store.slug if product else None)),
        participants=participants,
        last_message=last.body if last else None,
        last_message_at=last.created_at if last else None,
        unread_count=unread,
        created_at=conv.created_at,
    )


@router.get("", response_model=List[schemas.ConversationOut])
def list_conversations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convs = db.query(models.Conversation).all()
    result = [_conv_out(db, conv, current_user) for conv in convs if _is_participant(current_user, conv)]
    result.sort(key=lambda c: c.last_message_at or c.created_at, reverse=True)
    return result


@router.post(
    "",
    response_model=schemas.ConversationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: schemas.ConversationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(models.Product, payload.product_id)
    if not product or product.status != "active" or product.store.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan"
        )
    if product.store.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda tidak dapat chat dengan toko sendiri",
        )
    existing = (
        db.query(models.Conversation)
        .filter(
            models.Conversation.product_id == product.id,
            models.Conversation.order_id.is_(None),
            models.Conversation.buyer_id == current_user.id,
        )
        .first()
    )
    if existing:
        return _conv_out(db, existing, current_user)
    conv = models.Conversation(product_id=product.id, buyer_id=current_user.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return _conv_out(db, conv, current_user)


@router.get("/{conversation_id}/messages", response_model=List[schemas.MessageOut])
def list_messages(
    conversation_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_conv_or_403(db, current_user, conversation_id)
    messages = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conv.id)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    for msg in messages:
        if msg.sender_id != current_user.id and msg.read_at is None:
            msg.read_at = datetime.utcnow()
    db.commit()
    return [
        schemas.MessageOut(
            id=m.id,
            conversation_id=m.conversation_id,
            sender_id=m.sender_id,
            sender_name=m.sender.username if m.sender else None,
            body=m.body,
            read_at=m.read_at,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/{conversation_id}/messages", response_model=schemas.MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: int,
    payload: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_conv_or_403(db, current_user, conversation_id)
    msg = models.Message(
        conversation_id=conv.id,
        sender_id=current_user.id,
        body=payload.body,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return schemas.MessageOut(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender_id=msg.sender_id,
        sender_name=current_user.username,
        body=msg.body,
        read_at=msg.read_at,
        created_at=msg.created_at,
    )
