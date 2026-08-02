import random
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin, get_current_user
from app.services.notify import notify

router = APIRouter(prefix="/tickets", tags=["tickets"])

TICKET_STATUSES = ("open", "in_review", "resolved", "closed")


def _generate_ticket_code() -> str:
    return "TKT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def _can_access(ticket: models.Ticket, user: models.User) -> bool:
    if user.role == "admin":
        return True
    order = ticket.order
    return order.buyer_id == user.id or order.store.owner_id == user.id


def _get_ticket_or_403(db: Session, user: models.User, ticket_id: int) -> models.Ticket:
    ticket = db.get(models.Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tiket tidak ditemukan"
        )
    if not _can_access(ticket, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    return ticket


def _ticket_out(ticket: models.Ticket) -> schemas.TicketOut:
    return schemas.TicketOut(
        id=ticket.id,
        ticket_code=ticket.ticket_code,
        order_code=ticket.order.order_code,
        issue_type=ticket.issue_type,
        description=ticket.description,
        status=ticket.status,
        opened_by=ticket.opened_by.username if ticket.opened_by else None,
        store_name=ticket.order.store.name,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


def _ticket_detail_out(ticket: models.Ticket) -> schemas.TicketDetailOut:
    base = _ticket_out(ticket)
    return schemas.TicketDetailOut(
        **base.model_dump(),
        messages=[
            schemas.TicketMessageOut(
                id=m.id,
                ticket_id=m.ticket_id,
                sender_id=m.sender_id,
                sender_name=m.sender.username if m.sender else None,
                body=m.body,
                created_at=m.created_at,
            )
            for m in ticket.messages
        ],
        history=[
            schemas.TicketHistoryOut(
                id=h.id,
                status=h.status,
                note=h.note,
                actor=h.actor.username if h.actor else None,
                created_at=h.created_at,
            )
            for h in ticket.history
        ],
    )


def _record_status(db: Session, ticket: models.Ticket, status_: str, note: Optional[str], actor: models.User):
    db.add(
        models.TicketStatusHistory(
            ticket_id=ticket.id,
            status=status_,
            note=note,
            actor_id=actor.id,
        )
    )
    ticket.status = status_


def _notify_parties(db: Session, ticket: models.Ticket, title: str, body: str, link: str):
    recipients = {ticket.order.buyer_id, ticket.order.store.owner_id}
    for uid in recipients:
        notify(db, uid, "ticket", title, body, link)
    for adm in db.query(models.User).filter(models.User.role == "admin").all():
        notify(db, adm.id, "ticket", title, body, link)


@router.post("", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
def open_ticket(
    payload: schemas.TicketCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(models.Order)
        .filter(models.Order.order_code == payload.order_code)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pesanan tidak ditemukan"
        )
    if not (order.buyer_id == current_user.id or order.store.owner_id == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    if order.status == "pending_payment":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perselisihan hanya dapat diajukan untuk pesanan yang sudah dibayar",
        )
    active = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.order_id == order.id,
            models.Ticket.status.in_(("open", "in_review")),
        )
        .first()
    )
    if active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sudah ada tiket aktif untuk pesanan ini ({active.ticket_code})",
        )
    ticket = models.Ticket(
        ticket_code=_generate_ticket_code(),
        order_id=order.id,
        opened_by_id=current_user.id,
        issue_type=payload.issue_type,
        description=payload.description,
        status="open",
    )
    db.add(ticket)
    db.flush()
    _record_status(db, ticket, "open", "Tiket dibuka", current_user)
    link = f"/account/tickets/{ticket.ticket_code}"
    _notify_parties(
        db,
        ticket,
        f"Tiket perselisihan {ticket.ticket_code}",
        f"Tiket dibuka oleh {current_user.username} untuk pesanan {order.order_code}.",
        link,
    )
    db.commit()
    db.refresh(ticket)
    return _ticket_out(ticket)


@router.get("", response_model=List[schemas.TicketOut])
def list_tickets(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Ticket)
    tickets = query.order_by(models.Ticket.created_at.desc()).all()
    result = [t for t in tickets if _can_access(t, current_user)]
    if status_filter:
        result = [t for t in result if t.status == status_filter]
    return [_ticket_out(t) for t in result]


@router.get("/{ticket_id}", response_model=schemas.TicketDetailOut)
def get_ticket(
    ticket_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_ticket_or_403(db, current_user, ticket_id)
    return _ticket_detail_out(ticket)


@router.post("/{ticket_id}/messages", response_model=schemas.TicketMessageOut, status_code=status.HTTP_201_CREATED)
def add_message(
    ticket_id: int,
    payload: schemas.TicketMessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_ticket_or_403(db, current_user, ticket_id)
    if ticket.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tiket sudah ditutup",
        )
    msg = models.TicketMessage(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        body=payload.body,
    )
    db.add(msg)
    _notify_parties(
        db,
        ticket,
        f"Balasan tiket {ticket.ticket_code}",
        f"{current_user.username}: {payload.body[:120]}",
        f"/account/tickets/{ticket.ticket_code}",
    )
    db.commit()
    db.refresh(msg)
    return schemas.TicketMessageOut(
        id=msg.id,
        ticket_id=msg.ticket_id,
        sender_id=msg.sender_id,
        sender_name=current_user.username,
        body=msg.body,
        created_at=msg.created_at,
    )


@router.post("/{ticket_id}/status", response_model=schemas.TicketDetailOut)
def update_status(
    ticket_id: int,
    payload: schemas.TicketStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_ticket_or_403(db, current_user, ticket_id)
    new_status = payload.status
    if new_status not in TICKET_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Status tidak valid",
        )
    if ticket.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tiket sudah ditutup"
        )
    is_admin = current_user.role == "admin"
    is_opener = ticket.opened_by_id == current_user.id
    if new_status == "resolved" and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat menyelesaikan tiket",
        )
    if new_status == "in_review" and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat meninjau tiket",
        )
    if new_status == "closed" and not (is_admin or is_opener):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pembuka tiket atau admin yang dapat menutup tiket",
        )
    _record_status(db, ticket, new_status, payload.note, current_user)
    _notify_parties(
        db,
        ticket,
        f"Status tiket {ticket.ticket_code}: {new_status}",
        payload.note or f"Status berubah menjadi {new_status} oleh {current_user.username}.",
        f"/account/tickets/{ticket.ticket_code}",
    )
    db.commit()
    db.refresh(ticket)
    return _ticket_detail_out(ticket)


# ---------- Admin ----------

admin_router = APIRouter(prefix="/admin/tickets", tags=["tickets-admin"])


@admin_router.get("", response_model=List[schemas.TicketOut])
def admin_list_tickets(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    _admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Ticket)
    if status_filter:
        query = query.filter(models.Ticket.status == status_filter)
    tickets = query.order_by(models.Ticket.created_at.desc()).all()
    return [_ticket_out(t) for t in tickets]
