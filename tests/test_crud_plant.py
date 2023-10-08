import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.library.crud import create_plant, get_plants
from app.models.plant import Plant

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

# def test_get_plant(session: Session):



def test_create_plant(session: Session):
    plant = Plant(name_common="Test Plant 2", variety="Test Variety")
    db_plant = create_plant(session, plant)

    assert db_plant is not None

    assert db_plant.name_common == plant.name_common
    assert db_plant.variety == plant.variety
    assert db_plant.hints is None


def test_create_plant_duplicate(session: Session):
    plant = Plant(name_common="Test Plant", variety="Test Variety")
    db_plant_1 = create_plant(session, plant)

    assert db_plant_1 is not None

    db_plant_2 = create_plant(session, plant)

    assert db_plant_2 is None


def test_get_plants_single(session: Session):
    plant = Plant(name_common="Test Plant 1", variety="Test Variety")
    db_plant = create_plant(session, plant)

    assert db_plant is not None

    db_plants = get_plants(session)

    assert len(db_plants) == 1


def test_get_plants(session: Session):
    plant_1 = Plant(name_common="Test Plant 1", variety="Test Variety 1")
    db_plant_1 = create_plant(session, plant_1)

    plant_2 = Plant(name_common="Test Plant 2", variety="Test Variety 2")
    db_plant_2 = create_plant(session, plant_2)

    db_plants = get_plants(session)

    assert len(db_plants) == 2
