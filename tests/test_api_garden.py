import pytest
import random

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.main import app
from app.models.garden import Garden
from app.models.garden import GardenType, ClimaticZone

# from urllib import response


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


# Garden API tests


def test_create_garden(client: TestClient):
    response = client.post(
        "/api/gardens/",
        json={
            "name": "Test Garden"
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Garden"
    assert data["type"] is None
    assert data["location"] is None
    assert data["zone"] is None
    assert data["id"] is not None


def test_create_garden_with_type(client: TestClient):
    response = client.post(
        "/api/gardens/",
        json={
            "name": "Test Garden with type",
            "type": GardenType.INDOOR
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Garden with type"
    assert data["type"] == "Indoor"
    assert data["location"] is None
    assert data["zone"] is None
    assert data["id"] is not None

def test_create_garden_with_location(client: TestClient):
    response = client.post(
        "/api/gardens/",
        json={
            "name": "Test Garden with location",
            "location": "home"
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Garden with location"
    assert data["type"] is None
    assert data["location"] == "home"
    assert data["zone"] is None
    assert data["id"] is not None

def test_create_garden_with_zone(client: TestClient):
    response = client.post(
        "/api/gardens/",
        json={
            "name": "Test Garden with zone",
            "zone": ClimaticZone.TROPICAL
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Garden with zone"
    assert data["type"] is None
    assert data["location"] is None
    assert data["zone"] == "Tropical"
    assert data["id"] is not None

def test_read_gardens(
        session: Session,
        client: TestClient
):
    climatic_zone=random.choice(ClimaticZone.list())
    garden_type=random.choice(GardenType.list())
    garden_1 = Garden(
        name="Test Garden 1",
        climatic_zone=climatic_zone
    )
    session.add(garden_1)

    garden_2 = Garden(
        name="Test Garden 2",
        garden_type=garden_type
    )
    session.add(garden_2)

    session.commit()

    response = client.get("/api/gardens/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2

    assert data[0]["name"] == garden_1.name
    assert data[0]["type"] == garden_1.type
    assert data[0]["location"] == garden_1.location
    assert data[0]["zone"] == garden_1.zone
    assert data[0]["id"] == garden_1.id

    assert data[1]["name"] == garden_2.name
    assert data[1]["type"] == garden_2.type
    assert data[1]["location"] == garden_2.location
    assert data[1]["zone"] == garden_2.zone
    assert data[1]["id"] == garden_2.id
