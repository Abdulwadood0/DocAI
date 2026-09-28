from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from core.config import settings
from db.database import SessionDep
from db.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("id")

        if user_id is None:

            raise credentials_exception

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError):

        raise credentials_exception

    user = session.exec(
        select(User).where(User.id == user_id)
    ).first()
    if user is None:

        raise credentials_exception

    return user