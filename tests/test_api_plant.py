import pytest
import random

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.main import app
from app.models.plant import Plant
from app.models.bed import Bed
from app.models.bed import IrrigationZone

# Based on
# https://fastapi.tiangolo.com/tutorial/testing/
# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/


fake_secret_token = "coneofsilence"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
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
        json={"name_common": "test plant"},
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name_common"] == "test plant"
    assert data["variety"] is None
    assert data["name_botanical"] is None
    assert data["family_group"] is None
    assert data["harvest"] is None
    assert data["hints"] is None
    assert data["watch_for"] is None
    assert data["proven_varieties"] is None
    assert data["id"] is not None


def test_create_plant_incomplete(client: TestClient):
    """Attempt to create a plant without required name_common"""
    response = client.post(
        "/api/plants",
        json={"hints": "test"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_plant(
        session: Session,
        client: TestClient
):
    plant_1 = Plant(name_common="test plant", hints="test")
    session.add(plant_1)

    session.commit()

    response = client.get(f"/api/plants/{plant_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name_common"] == plant_1.name_common
    assert data["variety"] is None
    assert data["family_group"] is None
    assert data["hints"] == plant_1.hints
    assert data["id"] == plant_1.id


def test_read_plants(
        session: Session,
        client: TestClient
):
    """Test creation and retrieving multiple plants"""
    plant_1 = Plant(name_common="test plant 1", hints="test")
    session.add(plant_1)

    plant_2 = Plant(name_common="test plant 2")
    session.add(plant_2)

    session.commit()

    response = client.get("/api/plants/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json().get("items")

    assert len(data) == 2

    assert data[0]["name_common"] == plant_1.name_common
    assert data[0]["family_group"] == plant_1.family_group
    assert data[0]["hints"] == plant_1.hints
    assert data[0]["id"] == plant_1.id

    assert data[1]["name_common"] == plant_2.name_common
    assert data[1]["family_group"] == plant_2.family_group
    assert data[1]["hints"] == plant_2.hints
    assert data[1]["id"] == plant_2.id


def test_update_plant(
        session: Session,
        client: TestClient
):
    hints_original = "test"
    hints_updated = "updated"

    plant_1 = Plant(name_common="test plant", hints=hints_original)
    session.add(plant_1)
    session.commit()

    response = client.get(f"/api/plants/{plant_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name_common"] == plant_1.name_common
    assert data["family_group"] is None
    assert data["hints"] == hints_original
    assert data["id"] == plant_1.id

    response = client.patch(
        f"/api/plants/{plant_1.id}",
        json={"hints": hints_updated}
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name_common"] == plant_1.name_common
    assert data["family_group"] == plant_1.family_group
    assert data["hints"] == hints_updated
    assert data["id"] == plant_1.id


def test_delete_plant(
        session: Session,
        client: TestClient
):
    plant_1 = Plant(name_common="test plant 1")
    session.add(plant_1)

    plant_2 = Plant(name_common="test plant 2")
    session.add(plant_2)

    session.commit()

    response = client.get("/api/plants/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json().get("items")

    assert len(data) == 2

    assert data[0]["name_common"] == plant_1.name_common
    assert data[0]["id"] == plant_1.id

    assert data[1]["name_common"] == plant_2.name_common
    assert data[1]["id"] == plant_2.id

    response = client.delete(f"/api/plants/{plant_2.id}")

    assert response.status_code == status.HTTP_200_OK

    response = client.get("/api/plants/")

    data = response.json().get("items")

    assert len(data) == 1

    response = client.delete(f"/api/plants/{plant_1.id}")

    dp_plant = session.get(Plant, plant_1.id)

    assert response.status_code == status.HTTP_200_OK

    assert dp_plant is None
