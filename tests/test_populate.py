import pytest
import json
# import os.path
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models.plant import Plant


SCRIPT_PARENT_PATH = Path(__file__).parent
WORKSPACE_PATH = "/workspaces/garden-assistant"
DATA_DIR = "data"


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


def test_load_plant_data(session: session_fixture):
    data_filename = "plants.json"

    data_file_path = Path(WORKSPACE_PATH).joinpath(DATA_DIR, data_filename)

    assert Path(data_file_path).is_file

    with data_file_path.open() as file:
        plants_data = json.load(file)

    print(plants_data)

    assert isinstance(plants_data, list)

    for plant in plants_data:
        session.add(Plant(**plant))

    session.commit

    # assert False
