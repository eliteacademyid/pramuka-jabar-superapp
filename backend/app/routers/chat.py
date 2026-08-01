from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/conversations", tags=["chat"])


def _get_conv_or_403(
    db: Session, user: models.User, conversation_id: int
) -> models.Conversation:
    conv = db.get(models.Conversation, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Percakapan tidak ditemukan"
        )
    order = conv.order
    is_buyer = order.buyer_id == user.id
    is_seller = order.store.owner_id == user.id
    is_admin = user.role == "admin"
    if not (is_buyer or is_seller or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    return conv


def _conv_out(db: Session, conv: models.Conversation) -> schemas.ConversationOut:
    return schemas.ConversationOut(
        id=conv.id,
        order_code=conv.order.order_code,
        order_status=conv.order.status,
        created_at=conv.created_at,
        participants=[
            conv.order.store.owner.username,
            conv.order.buyer.username,
            *[u.username for u in db.query(models.User).filter(models.User.role == "admin").all()],
        ],
    )


@router.get("", response_model=List[schemas.ConversationOut])
def list_conversations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convs = db.query(models.Conversation).all()
    result = []
    for conv in convs:
        order = conv.order
        is_buyer = order.buyer_id == current_user.id
        is_seller = order.store.owner_id == current_user.id
        is_admin = current_user.role == "admin"
        if is_buyer or is_seller or is_admin:
            result.append(_conv_out(db, conv))
    return result


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
