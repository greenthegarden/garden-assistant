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
from app.models.garden import Garden


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


# Garden Bed API tests

# def test_create_bed_no_auth(client: TestClient):
#     response = client.post("/api/beds",
#                            json={"name": "Test Plot",
#                            "soil_type": SoilType.LOAM,
#                            "irrigation_zone": IrrigationZone.VEGETABLES}
#     )
#     assert response.status_code == status.HTTP_403_FORBIDDEN

#     data = response.json()
#     print(data)


def test_create_bed(client: TestClient):
    response = client.post(
        "/api/beds/",
        json={
            "name": "Test Bed",
            "soil_type": SoilType.LOAM,
            "irrigation_zone": IrrigationZone.VEGETABLES,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == "Test Bed"
    assert data["soil_type"] == "Loam"
    assert data["irrigation_zone"] == "Vegetables"
    assert data["id"] is not None


def test_create_bed_incomplete(client: TestClient):
    """Attempt to create a bed without required name"""
    response = client.post(
        "/api/beds",
        json={"soil_type": SoilType.LOAM, "irrigation_zone": IrrigationZone.VEGETABLES}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_beds(
        session: Session,
        client: TestClient
):
    """Test creation and retrieving multiple garden beds"""
    irrigation_zone=random.choice(IrrigationZone.list())
    soil_type=random.choice(SoilType.list())

    bed_1 = Bed(
        name="Test Garden Bed 1",
        irrigation_zone=irrigation_zone
    )
    session.add(bed_1)

    bed_2 = Bed(
        name="Test Garden Bed 2",
        soil_type=soil_type
    )
    session.add(bed_2)

    session.commit()

    response = client.get("/api/beds/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 2

    assert data[0]["name"] == bed_1.name
    assert data[0]["soil_type"] == bed_1.soil_type
    assert data[0]["irrigation_zone"] == bed_1.irrigation_zone
    assert data[0]["id"] == bed_1.id

    assert data[1]["name"] == bed_2.name
    assert data[1]["soil_type"] == bed_2.soil_type
    assert data[1]["irrigation_zone"] == bed_2.irrigation_zone
    assert data[1]["id"] == bed_2.id


def test_read_bed(
        session: Session,
        client: TestClient
):
    bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
    session.add(bed_1)
    session.commit()

    response = client.get(f"/api/beds/{bed_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == bed_1.name
    assert data["soil_type"] == bed_1.soil_type
    assert data["irrigation_zone"] == bed_1.irrigation_zone
    assert data["id"] == bed_1.id


def test_read_bed_with_garden(
        session: Session,
        client: TestClient
):
    garden_1 = Garden(name="Test Garden")
    session.add(garden_1)

    irrigation_zone=random.choice(IrrigationZone.list())

    bed_1 = Bed(
        name="Vegetable Plot",
        irrigation_zone=irrigation_zone,
        garden=garden_1
    )
    session.add(bed_1)

    session.commit()

    response = client.get(f"/api/beds/{bed_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["name"] == bed_1.name
    assert data["soil_type"] == bed_1.soil_type
    assert data["irrigation_zone"] == bed_1.irrigation_zone
    assert data["id"] == bed_1.id
    assert data["garden"]["name"] == garden_1.name


def test_update_bed(
        session: Session,
        client: TestClient
):
    bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
    session.add(bed_1)
    session.commit()

    response = client.get(f"/api/beds/{bed_1.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert isinstance(data, dict)
    assert data["name"] == bed_1.name
    assert data["soil_type"] is None
    assert data["id"] is not None

    response = client.patch(
        f"/api/beds/{bed_1.id}",
        json = {"name": "Updated Bed"},
        # json = {"soil_type": SoilType.CLAY}
    )

    assert response.status_code == status.HTTP_201_CREATED

    # data = response.json()

    # assert data["name"] == bed_1.name
    # assert data["soil_type"] == "Clay"
    # assert data["irrigation_zone"] == bed_1.irrigation_zone
    # assert data["id"] == bed_1.id


def test_delete_bed(
        session: Session,
        client: TestClient
):
    bed_1 = Bed(name="Vegetable Plot", irrigation_zone=IrrigationZone.VEGETABLES)
    session.add(bed_1)

    session.commit()

    response = client.delete(f"/api/beds/{bed_1.id}")

    assert response.status_code == status.HTTP_200_OK

    dp_bed = session.get(Bed, bed_1.id)

    assert dp_bed is None
