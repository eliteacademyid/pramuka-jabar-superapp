from datetime import date
from typing import Optional

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/member", tags=["member"])


@router.get("/card", response_model=schemas.MemberCardOut)
def get_member_card(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get digital membership card for authenticated user.
    Returns complete card information including verification token.
    """
    return current_user


@router.get("/qrcode", response_model=schemas.QRCodeOut)
def get_qrcode(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate QR code data for member verification.
    Returns verification URL that can be embedded in QR code.
    """
    if not current_user.verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token verifikasi tidak tersedia",
        )
    
    # Generate verification URL
    # In production, replace with actual domain
    verification_url = f"http://localhost:5173/verify/{current_user.verification_token}"
    
    # QR Code URL is the same as verification URL
    # Frontend will use this to generate QR code image
    return {
        "qr_code_url": verification_url,
        "verification_url": verification_url,
    }


@router.get("/verify/{token}", response_model=schemas.VerificationOut)
def verify_member(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Public endpoint to verify member by token.
    No authentication required.
    Returns limited member information without sensitive data.
    """
    try:
        # Query user by verification token
        user = (
            db.query(models.User)
            .filter(models.User.verification_token == token)
            .first()
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token verifikasi tidak valid atau anggota tidak ditemukan",
            )
        
        # Check if membership is still valid
        if user.valid_until and user.valid_until < date.today():
            # Update status to expired if past valid date
            if user.membership_status != "expired":
                user.membership_status = "expired"
                db.commit()
        
        # Return only public information
        return {
            "nama_lengkap": user.nama_lengkap,
            "nomor_anggota": user.nomor_anggota,
            "golongan": user.golongan,
            "kwartir": user.kwartir,
            "membership_status": user.membership_status,
        }
        
    except ValueError:
        # Invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format token tidak valid",
        )
