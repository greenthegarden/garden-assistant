import pytest
import random

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.main import app
from app.models.planting import Planting
from app.models.bed import Bed, IrrigationZone
from app.models.plant import Plant


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


# Garden Planting API tests


def test_create_planting(client: TestClient):
    response = client.post(
        "/api/plantings/",
        json={"name": "Test Planting 1"}
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Planting 1"
    assert data["notes"] is None
    assert data["bed_id"] is None
    assert data["id"] is not None


def test_create_planting_incomplete(client: TestClient):
    # attempt to create a planting with no plant
    response = client.post("/api/plantings", json={"notes": "Test note"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_plantings(
        session: Session,
        client: TestClient
):
    planting_1 = Planting(name="Test Planting 1", notes="Test note")
    session.add(planting_1)

    planting_2 = Planting(name="Test Planting 2")
    session.add(planting_2)

    session.commit()

    response = client.get("/api/plantings/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2

    assert data[0]["name"] == planting_1.name
    assert data[0]["notes"] == planting_1.notes
    assert data[0]["id"] == planting_1.id

    assert data[1]["name"] == planting_2.name
    assert data[1]["notes"] == planting_2.notes
    assert data[1]["id"] == planting_2.id


def test_read_planting(
        session: Session,
        client: TestClient
):
    planting_1 = Planting(name="Test Planting 1", notes="Test note")
    session.add(planting_1)

    session.commit()

    response = client.get(f"/api/plantings/{planting_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == planting_1.name
    assert data["notes"] == planting_1.notes
    assert data["id"] == planting_1.id


def test_read_planting_with_bed(
        session: Session,
        client: TestClient
):
    irrigation_zone=random.choice(IrrigationZone.list())

    bed_1 = Bed(name="Test Bed", irrigation_zone=irrigation_zone)
    session.add(bed_1)

    planting_1 = Planting(name="Test Planting", bed=bed_1)
    session.add(planting_1)

    session.commit()

    response = client.get(f"/api/beds/{bed_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == bed_1.name

    response = client.get(f"/api/plantings/{planting_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == planting_1.name
    assert data["notes"] == planting_1.notes
    assert data["bed_id"] == planting_1.bed_id
    assert data["id"] == planting_1.id
    assert data["bed"]["name"] == bed_1.name


def test_read_planting_with_plant(
        session: Session,
        client: TestClient
):
    plant = Plant(name_common="Test Plant", variety="Test Variety")
    session.add(plant)
    
    planting_1 = Planting(name="Test Planting", plants=[plant])
    session.add(planting_1)

    session.commit()

    response = client.get(f"/api/plantings/{planting_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    print(data)

    assert data["name"] == planting_1.name
    assert data["notes"] == planting_1.notes
    assert data["bed_id"] == planting_1.bed_id
    assert data["id"] == planting_1.id


def test_update_planting(
        session: Session,
        client: TestClient
):
    notes_original = "Test note"
    notes_updated = "Updated note"

    planting_1 = Planting(name="Test Planting 1", notes=notes_original)
    session.add(planting_1)

    session.commit()

    response = client.get(f"/api/plantings/{planting_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == planting_1.name
    assert data["notes"] == notes_original
    assert data["id"] == planting_1.id

    response = client.patch(
        f"/api/plantings/{planting_1.id}",
        json={"notes": notes_updated},
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == planting_1.name
    assert data["notes"] == notes_updated
    assert data["id"] == planting_1.id


def test_delete_planting(
        session: Session,
        client: TestClient
):
    planting_1 = Planting(name="Test Planting 1", notes="Test note")
    session.add(planting_1)

    session.commit()

    response = client.delete(f"/api/plantings/{planting_1.id}")

    assert response.status_code == status.HTTP_200_OK

    dp_planting = session.get(Planting, planting_1.id)

    assert dp_planting is None
