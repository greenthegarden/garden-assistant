from sqlmodel import Session, select

from ..database.database import engine
from ..models.user import User


def select_all_users():
    with Session(engine) as session:
        statement = select(User)
        result = session.exec(statement).all()
        return result


def find_user(name):
    with Session(engine) as session:
        statement = select(User).where(User.username == name)
        return session.exec(statement).first()
