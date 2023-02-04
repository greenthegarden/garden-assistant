from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
# from urllib import response

from main import app, get_session

# Based on https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/


@pytest.fixture(name="session")
def session_fixture():
  engine = create_engine(
    "sqlite:///testing.db",
    connect_args={"check_same_thread": False},
    poolclass = StaticPool
  )
  SQLModel.metadata.create_all(engine)
  with Session(engine) as session:
    yield session
  
  
@pytest.fixture(name="client")
def client_fixture(session: Session):
  def get_session_override():
    return session

  app.dependency_overrides[get_session] = get_session_override

  client = TestClient(app)
  yield client
  app.dependency_overrides.clear() 
  
  
def test_create_planting(client: TestClient):
    response = client.post(
      "/plantings",
      json={"plant": "cucumber"}
    )
    data = response.json()
    print(data)
    
    assert response.status_code == 201
    assert data["plant"] == "cucumber"
    assert data["notes"] is None
    assert data["id"] is not None

# def test_create_planting_incomplete(client: TestClient):
#   # no name
#   response = client.post(
#     "/create_planting",
#     json={"notes": "test"}
#   )
#   assert response.status_code == 422
  
  