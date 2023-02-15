from fastapi.testclient import TestClient
import pytest
import random
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from urllib import response

from app.main import app, get_session
from app.models.garden_models import Bed, Planting
from app.models.garden_models import SoilType, IrrigationZone

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


# Garden Bed API tests

def test_create_bed(client: TestClient):
    response = client.post(
      "/api/beds",
      json={"name": "Vegetable Plot", "soil_type": SoilType.LOAM, "irrigation_zone": IrrigationZone.VEGETABLES}
    )
    data = response.json()
    print(data)
    
    assert response.status_code == 200
    assert data["name"] == "Vegetable Plot"
    assert data["soil_type"] == "Loam"
    assert data["irrigation_zone"] == "Vegetables"
    assert data["id"] is not None


def test_create_bed_incomplete(client: TestClient):
  # attempt to create a bed with no name
  response = client.post(
    "/api/beds",
    json={"soil_type": SoilType.LOAM, "irrigation_zone": IrrigationZone.VEGETABLES}
  )
  assert response.status_code == 422
  

def test_read_beds(session: Session, client: TestClient):
  irrigation_zone=random.choice(IrrigationZone.list())
  soil_type=random.choice(SoilType.list())
  bed_1 = Bed(name="Vegetable Plot", irrigation_zone=irrigation_zone)
  bed_2 = Bed(name="Seedlings", soil_type=soil_type)
  session.add(bed_1)
  session.add(bed_2)
  session.commit()
  
  response = client.get("/api/beds/")
  data = response.json()
  
  assert response.status_code == 200
  
  assert len(data) == 2
  assert data[0]["name"] == bed_1.name
  assert data[0]["soil_type"] == bed_1.soil_type
  assert data[0]["irrigation_zone"] == bed_1.irrigation_zone
  assert data[0]["id"] == bed_1.id
  assert data[1]["name"] == bed_2.name
  assert data[1]["soil_type"] == bed_2.soil_type
  assert data[1]["irrigation_zone"] == bed_2.irrigation_zone
  assert data[1]["id"] == bed_2.id


def test_read_bed(session: Session, client: TestClient):
  bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
  session.add(bed_1)
  session.commit()
  
  response = client.get(f"/api/beds/{bed_1.id}")
  data = response.json()
  
  assert response.status_code == 200
  
  assert data["name"] == bed_1.name
  assert data["soil_type"] == bed_1.soil_type
  assert data["irrigation_zone"] == bed_1.irrigation_zone
  assert data["id"] == bed_1.id
  

def test_update_bed(session: Session, client: TestClient):
  bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
  session.add(bed_1)
  session.commit()
  
  response = client.patch(f"/api/beds/{bed_1.id}", json={"soil_type": SoilType.CLAY})
  data = response.json()
  
  assert response.status_code == 200
  
  assert data["name"] == bed_1.name
  assert data["soil_type"] == "Clay"
  assert data["irrigation_zone"] == bed_1.irrigation_zone
  assert data["id"] == bed_1.id
  

def test_delete_bed(session: Session, client: TestClient):
  bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
  session.add(bed_1)
  session.commit()
  
  response = client.delete(f"/api/beds/{bed_1.id}")

  dp_bed = session.get(Bed, bed_1.id)
    
  assert response.status_code == 200
  
  assert dp_bed is None


# Garden Planting API tests

def test_create_planting(client: TestClient):
    response = client.post(
      "/api/plantings",
      json={"plant": "cucumber"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["plant"] == "cucumber"
    assert data["notes"] is None
    assert data["id"] is not None


def test_create_planting_incomplete(client: TestClient):
  # attempt to create a planting with no plant
  response = client.post(
    "/api/plantings",
    json={"notes": "test"}
  )
  assert response.status_code == 422
  

def test_read_plantings(session: Session, client: TestClient):
  planting_1 = Planting(plant="apple", notes="test")
  planting_2 = Planting(plant="corn")
  session.add(planting_1)
  session.add(planting_2)
  session.commit()
  
  response = client.get("/api/plantings/")
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
  
  response = client.get(f"/api/plantings/{planting_1.id}")
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
  
  response = client.patch(f"/api/plantings/{planting_1.id}", json={"notes": "updated"})
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
  
  response = client.delete(f"/api/plantings/{planting_1.id}")

  dp_planting = session.get(Planting, planting_1.id)
    
  assert response.status_code == 200
  
  assert dp_planting is None


def test_read_planting_with_bed(session: Session, client: TestClient):
  bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
  session.add(bed_1)
  session.commit()
  planting_1 = Planting(plant="corn", bed_id=bed_1.id)
  session.add(planting_1)
  session.commit()

  response = client.get(f"/api/plantings/{planting_1.id}")
  data = response.json()
  
  assert response.status_code == 200
  
  assert data["plant"] == planting_1.plant
  assert data["variety"] == planting_1.variety
  assert data["notes"] == planting_1.notes
  assert data["bed_id"] == planting_1.bed_id
  assert data["id"] == planting_1.id
  assert planting_1.bed.name == bed_1.name
  