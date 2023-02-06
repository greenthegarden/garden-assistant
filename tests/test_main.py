from urllib import response
from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
# from urllib import response

from main import app, get_session
from models import Planting

# Based on https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/


@pytest.fixture(name="session")
def session_fixture():
  engine = create_engine(
    "sqlite://",
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
    
    assert response.status_code == 200
    assert data["plant"] == "cucumber"
    assert data["notes"] is None
    assert data["id"] is not None


def test_create_planting_incomplete(client: TestClient):
  # no name
  response = client.post(
    "/plantings",
    json={"notes": "test"}
  )
  assert response.status_code == 422
  

def test_read_plantings(session: Session, client: TestClient):
  planting_1 = Planting(plant="apple", notes="test")
  planting_2 = Planting(plant="corn")
  session.add(planting_1)
  session.add(planting_2)
  session.commit()
  
  response = client.get("/plantings/")
  data = response.json()
  
  assert response.status_code == 200
  
  assert len(data) == 2
  assert data[0]["plant"] == planting_1.plant
  assert data[0]["variety"] == planting_1.variety
  assert data[0]["notes"] == planting_1.notes
  assert data[0]["id"] == planting_1.id
  assert data[1]["plant"] == planting_2.plant
  assert data[1]["variety"] == planting_2.variety
  assert data[1]["notes"] == planting_2.notes
  assert data[1]["id"] == planting_2.id


def test_read_planting(session: Session, client: TestClient):
  planting_1 = Planting(plant="apple", notes="test")
  session.add(planting_1)
  session.commit()
  
  response = client.get(f"/plantings/{planting_1.id}")
  data = response.json()
  
  assert response.status_code == 200
  
  assert data["plant"] == planting_1.plant
  assert data["variety"] == planting_1.variety
  assert data["notes"] == planting_1.notes
  assert data["id"] == planting_1.id
  

def test_update_planting(session: Session, client: TestClient):
  planting_1 = Planting(plant="apple", notes="test")
  session.add(planting_1)
  session.commit()
  
  response = client.patch(f"/plantings/{planting_1.id}", json={"notes": "updated"})
  data = response.json()
  
  assert response.status_code == 200
  
  assert data["plant"] == planting_1.plant
  assert data["variety"] == planting_1.variety
  assert data["notes"] == "updated"
  assert data["id"] == planting_1.id
  

def test_delete_planting(session: Session, client: TestClient):
  planting_1 = Planting(plant="apple", notes="test")
  session.add(planting_1)
  session.commit()
  
  response = client.delete(f"/plantings/{planting_1.id}")

  dp_planting = session.get(Planting, planting_1.id)
    
  assert response.status_code == 200
  
  assert dp_planting is None
