from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | (models.User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username atau email sudah terdaftar",
        )
    
    # Create new user
    hashed_password = auth.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        nama_lengkap=user_data.nama_lengkap,
        hashed_password=hashed_password,
        role_id=2,  # Default to staff role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    # Find user by username or email
    user = db.query(models.User).filter(
        (models.User.username == credentials.username_or_email) |
        (models.User.email == credentials.username_or_email)
    ).first()
    
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/email atau password salah",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun Anda tidak aktif",
        )
    
    # Create tokens
    access_token = auth.create_access_token({"sub": str(user.id), "username": user.username})
    refresh_token = auth.create_refresh_token({"sub": str(user.id), "username": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(request: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    payload = auth.verify_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kadaluarsa",
        )
    
    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan atau tidak aktif",
        )
    
    # Create new tokens
    access_token = auth.create_access_token({"sub": str(user.id), "username": user.username})
    refresh_token = auth.create_refresh_token({"sub": str(user.id), "username": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: models.User = Depends(get_current_user)):
    """Logout user (client-side token deletion)"""
    # In this simple implementation, logout is handled on client side
    # by deleting the token. In production, you might want to implement
    # token blacklisting
    return None


@router.get("/me", response_model=schemas.UserDetailResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current logged-in user information"""
    return current_user


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
