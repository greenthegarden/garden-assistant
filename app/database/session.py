from sqlmodel import Session
from app.database.database import engine

# See https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/

def get_session():
    with Session(engine) as session:
        yield session
