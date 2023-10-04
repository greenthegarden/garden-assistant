import json
from pathlib import Path

from fastapi import Depends
from sqlmodel import Session

from .database.session import get_session
from .database.database import engine
from .models.plant import Plant, PlantCreate

WORKSPACE_BASE_PATH = "/workspaces/garden-assistant"
DATA_DIR = "data"

# SCRIPT_PARENT_PATH = pathlib.Path(__file__).parent

# def get_data_path(data_class: str):
#     data_filename = 
#     data_dir_path = pathlib.Path(SCRIPT_PARENT_PATH, DATA_DIR)
#     print(data_dir_path)

# def load_json_data(json_filename: str):
#     print(data_dir_path)
#     # p = pathlib.Path('path/to/file')
    # if p.is_file():
    #     try:
    #         with p.open() as f:
    #             plants_data = json.load(file)
    #     except OSError:
    #         print('Well darn.')
    # else:
    #     raise FileNotFoundError(path)
    # try:
    #     plant_data_file = os.path.join(DATA_BASE_PATH, json_filename)

    # with open(plant_data_file, mode='rt', encoding='utf-8') as file:

    # print(type(plants_data))
    # return plants_init

# def load_plant_data():
#     plant_data_filename = "plants.json"
#     plant_data_file = os.path.join(DATA_BASE_PATH, plant_data_filename)

#     with open(plant_data_file, mode='rt', encoding='utf-8') as file:
#         plants_data = json.load(file)

#     print(type(plants_data))
#     return plants_data

# def create_plant(plant_in: dict) -> PlantCreate:
#     name_common = plant_in.get("name_common")
#     plant = Plant(name_common=name_common )
#     for key, val in plant_in.items():
#         setattr(plant, key, val)
#     return plant

# def create_plant_db(plant: Plant):
#     with Session(engine) as session:
#         session.add(plant)
#         session.commit()
#         session.refresh(plant)


def populate_plants():
    data_filename = "plants.json"

    data_file_path = Path(WORKSPACE_BASE_PATH).joinpath(DATA_DIR, data_filename)

    # assert Path(data_file_path).is_file

    with data_file_path.open() as file:
        plants_data = json.load(file)

    print(plants_data)

    # assert isinstance(plants_data, list)

    with Session(engine) as session:
        for plant in plants_data:
            session.add(Plant(**plant))

        session.commit()


    # assert False

if __name__ == '__main__':
    """Creates the table if this file is run independently, as a script"""
    populate_plants()
