from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select

from ..auth.auth import AuthHandler
from ..database.session import get_session
from ..models.user import User, UserInput, UserLogin


user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post(
        "/registration",
        status_code=status.HTTP_201_CREATED,
        tags=["Users API"]
)
def register(
    *,
    session: Session = Depends(get_session),
    user: UserInput
):
    """Register a new user"""
    statement = select(User)
    db_users = session.exec(statement).all()
    if any(x.username == user.username for x in db_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username {user.username} is taken"
        )
    hashed_pwd = auth_handler.get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_pwd, email=user.email)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    db_user = session.get(User, new_user.id)
    user_data = jsonable_encoder(db_user)
    return {'user': user_data}


@user_router.post(
        "/login",
        tags=["Users API"]
)
def login(
    *,
    session: Session = Depends(get_session),
    user: UserLogin
):
    """Login as an existing user"""
    statement = select(User).where(User.username == user.username)
    db_user = session.exec(statement).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username and/or password"
        )
    verified = auth_handler.verify_password(user.password, db_user.password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username and/or password"
        )
    token = auth_handler.encode_token(db_user.username)
    return {'token': token}


@user_router.get(
        "/users/current",
        tags=["Users API"]
)
def get_current_user(
    *,
    user: User = Depends(auth_handler.get_current_user)
):
    """Return the current user"""
    return user
