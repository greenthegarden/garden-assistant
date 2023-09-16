import pytest
import random

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.main import app
from app.models.plant import Plant


# Based on
# https://fastapi.tiangolo.com/tutorial/testing/
# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/


fake_secret_token = "coneofsilence"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
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


# Garden Plant API tests

def test_create_plant(client: TestClient):
    response = client.post(
        "/api/plants/",
        json={"name_common": "cucumber"},
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name_common"] == "cucumber"
    assert data["name_botanical"] is None
    assert data["family_group"] is None
    assert data["harvest"] is None
    assert data["hints"] is None
    assert data["watch_for"] is None
    assert data["proven_varieties"] is None
    assert data["id"] is not None


# def test_create_plant_incomplete(client: TestClient):
#     # attempt to create a plant with no plant
#     response = client.post(
#         "/api/plants",
#         json={"notes": "test"}
#     )
#     assert response.status_code == 422


# def test_read_plants(session: Session, client: TestClient):
#     plant_1 = plant(plant="apple", notes="test")
#     plant_2 = plant(plant="corn")
#     session.add(plant_1)
#     session.add(plant_2)
#     session.commit()

#     response = client.get("/api/plants/")
#     data = response.json()

#     assert response.status_code == status.HTTP_200_OK

#     assert len(data) == 2
#     assert data[0]["plant"] == plant_1.plant
#     assert data[0]["variety"] == plant_1.variety
#     assert data[0]["notes"] == plant_1.notes
#     assert data[0]["id"] == plant_1.id
#     assert data[1]["plant"] == plant_2.plant
#     assert data[1]["variety"] == plant_2.variety
#     assert data[1]["notes"] == plant_2.notes
#     assert data[1]["id"] == plant_2.id


# # def test_read_plant(session: Session, client: TestClient):
# #     plant_1 = plant(plant="apple", notes="test")
# #     session.add(plant_1)
# #     session.commit()

# #     response = client.get(f"/api/plants/{plant_1.id}")
# #     data = response.json()

# #     assert response.status_code == status.HTTP_200_OK

# #     assert data["plant"] == plant_1.plant
# #     assert data["variety"] == plant_1.variety
# #     assert data["notes"] == plant_1.notes
# #     assert data["id"] == plant_1.id


# # def test_update_plant(session: Session, client: TestClient):
# #     plant_1 = plant(plant="apple", notes="test")
# #     session.add(plant_1)
# #     session.commit()

# #     response = client.patch(f"/api/plants/{plant_1.id}",
# #                             json={"notes": "updated"})
# #     data = response.json()

# #     assert response.status_code == status.HTTP_201_CREATED

# #     assert data["plant"] == plant_1.plant
# #     assert data["variety"] == plant_1.variety
# #     assert data["notes"] == "updated"
# #     assert data["id"] == plant_1.id


# # def test_delete_plant(session: Session, client: TestClient):
# #     plant_1 = plant(plant="apple", notes="test")
# #     session.add(plant_1)
# #     session.commit()

# #     response = client.delete(f"/api/plants/{plant_1.id}")

# #     dp_plant = session.get(plant, plant_1.id)

# #     assert response.status_code == status.HTTP_200_OK

# #     assert dp_plant is None


# # def test_read_plant_with_bed(session: Session, client: TestClient):
# #     bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
# #     session.add(bed_1)
# #     session.commit()
# #     plant_1 = plant(plant="corn", bed_id=bed_1.id)
# #     session.add(plant_1)
# #     session.commit()

# #     response = client.get(f"/api/plants/{plant_1.id}")
# #     data = response.json()

# #     assert response.status_code == status.HTTP_200_OK

# #     assert data["plant"] == plant_1.plant
# #     assert data["variety"] == plant_1.variety
# #     assert data["notes"] == plant_1.notes
# #     assert data["bed_id"] == plant_1.bed_id
# #     assert data["id"] == plant_1.id
# #     assert plant_1.bed.name == bed_1.name
