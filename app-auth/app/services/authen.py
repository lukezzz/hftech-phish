from sqlalchemy.orm import Session
from app.models import UserAccount, Role
from app.common.security import verify_password
from typing import Any

from fastapi.exceptions import HTTPException


def auth_user(db: Session, email: str, password: str) -> Any:
    user = db.query(UserAccount).filter_by(email=email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Bad email or password",
        )
    if not verify_password(password, user.password_hashed):
        raise HTTPException(
            status_code=401,
            detail="Bad email or password",
        )
    return user