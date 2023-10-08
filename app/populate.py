import json
from pathlib import Path

from sqlmodel import Session

from .database.database import engine, create_db_and_tables
from .helpers.plant import create_plants

WORKSPACE_BASE_PATH = "/workspaces/garden-assistant"
DATA_DIR = "data"

def populate_plants():
    data_filename = "plants.json"

    data_file_path = Path(WORKSPACE_BASE_PATH).joinpath(DATA_DIR, data_filename)

    with data_file_path.open() as file:
        plants_data = json.load(file)

    with Session(engine) as session:
        create_plants(session, plants_data)


if __name__ == '__main__':
    """Creates the table if this file is run independently, as a script"""
    print("Creating database and tables...")
    create_db_and_tables()
    populate_plants()
