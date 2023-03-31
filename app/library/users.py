from sqlmodel import Session, select

from app.database.database import engine
from app.models.user_models import User


def select_all_users():
  with Session(engine) as session:
    statement = select(User)
    result = session.exec(statement).all()
    return result


def find_user(name):
  with Session(engine) as session:
      statement = select(User).where(User.username == name)
      return session.exec(statement).first()
