"""JWT authentication utilities."""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.user import User

security = HTTPBearer()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(plain), hashed)


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)
    return jwt.encode({"sub": username, "exp": expire}, settings.jwt_secret, algorithm="HS256")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
