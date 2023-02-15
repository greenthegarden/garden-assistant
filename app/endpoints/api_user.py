from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select

from app.auth.auth import AuthHandler
from app.database.session import get_session
from app.models.user_models import UserInput, User, UserLogin


user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post("/registration", status_code=201, tags=["Users API"],
                  description="Register a new user")
def register(*, session: Session = Depends(get_session), user: UserInput):
  statement = select(User)
  db_users = session.exec(statement).all()
  if any(x.username == user.username for x in db_users):
    raise HTTPException(status_code=400, detail="Username is taken")
  hashed_pwd = auth_handler.get_password_hash(user.password)
  new_user = User(username=user.username, password=hashed_pwd, email=user.email)
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  db_user = session.get(User, new_user.id)
  user_data = jsonable_encoder(db_user)
  return {'user': user_data}


@user_router.post("/login", tags=["Users API"])
def login(*, session: Session = Depends(get_session), user: UserLogin):
  statement = select(User).where(User.username == user.username)
  user_db = session.exec(statement).first()
  if not user_db:
    raise HTTPException(status_code=401, detail="Invalid username and/or password")
  verified = auth_handler.verify_password(user.password, user_db.password)
  if not verified:
    raise HTTPException(status_code=401, detail="Invalid username and/or password")
  token = auth_handler.encode_token(user_db.username)
  return {'token': token}


@user_router.get("/users/me", tags=["Users API"])
def get_current_user(*, session: Session = Depends(get_session), user: User = Depends(auth_handler.get_current_user)):
  return user
