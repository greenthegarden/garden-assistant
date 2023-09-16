import pytest
import random

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.main import app
from app.models.bed import IrrigationZone, SoilType
from app.models.bed import Bed
from app.models.garden import GardenType, ClimaticZone

# from urllib import response


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


# Garden API tests


def test_create_garden(client: TestClient):
    response = client.post(
        "/api/gardens/",
        json={"name": "Test Garden"},
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
        json={"name": "Test Garden with type", "type": GardenType.INDOOR},
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
        json={"name": "Test Garden with location", "location": "home"},
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
        json={"name": "Test Garden with zone", "zone": ClimaticZone.TROPICAL},
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Garden with zone"
    assert data["type"] is None
    assert data["location"] is None
    assert data["zone"] == "Tropical"
    assert data["id"] is not None
