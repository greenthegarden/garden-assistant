import pytest

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database.session import get_session
from app.library.crud import create_plant


# Based on
# https://fastapi.tiangolo.com/tutorial/testing/
# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/


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


# Garden Plant API tests


def test_create_plant(session: Session):
    plant = {"name_common": "Test Plant", "variety": "Test Variety"}
    db_plant = create_plant(session, plant)

    assert db_plant is not None

    assert False


# def test_create_plant_duplicate_name(client: TestClient):
#     """Attempt to create a plant with duplicate name_common"""
#     response = client.post(
#         "/api/plants/",
#         json={"name_common": "Test Plant", "variety": "Test Variety 1"},
#     )
#     assert response.status_code == status.HTTP_201_CREATED

#     response = client.post(
#         "/api/plants/",
#         json={"name_common": "Test Plant", "variety": "Test Variety 2"},
#     )
#     assert response.status_code == status.HTTP_201_CREATED


# def test_create_plant_duplicate_name_and_variety(client: TestClient):
#     """Attempt to create a plant with duplicate name_common and variety"""
#     response = client.post(
#         "/api/plants/",
#         json={"name_common": "Test Plant", "variety": "Test Variety"},
#     )
#     assert response.status_code == status.HTTP_201_CREATED

#     response = client.post(
#         "/api/plants/",
#         json={"name_common": "Test Plant", "variety": "Test Variety"},
#     )
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
