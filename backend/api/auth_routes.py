from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import verify_password, create_token, get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_token(user.username))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
