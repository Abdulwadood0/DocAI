from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select

from core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from db.database import SessionDep
from db.models.user import User
from schemas.auth import Token, UserCreate, UserPublic
from typing import Annotated
from fastapi import Depends
from api.deps import get_current_user
from core.oauth import oauth

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)



@router.get("/me", response_model=UserPublic)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for(
        "google_callback"
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: SessionDep,
):
    token = await oauth.google.authorize_access_token(request)

    user_info = token["userinfo"]

    google_id = user_info["sub"]
    email = user_info["email"]

    user = session.exec(
        select(User).where(User.google_id == google_id)
    ).first()

    if not user:
        user = session.exec(
            select(User).where(User.email == email)
        ).first()

    if not user:
        user = User(
            email=email,
            google_id=google_id,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

    elif not user.google_id:
        user.google_id = google_id

        session.add(user)
        session.commit()
        session.refresh(user)

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }



@router.post(
    "/register",
    response_model=UserPublic,
    status_code=201,
)
def register(
    user_data: UserCreate,
    session: SessionDep,
):
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    user_data: UserCreate,
    session: SessionDep,
):
    user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return Token(
        access_token=access_token,
        token_type="bearer",
    )