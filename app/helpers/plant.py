"""Reusable CRUD functions to interact with the data in the database.

Based on https://fastapi.tiangolo.com/tutorial/sql-databases/
"""
from typing import List

from sqlmodel import Session, select

from ..models.plant import Plant, PlantCreate, PlantRead
from ..models.relationships import PlantReadWithPlanting


def get_plant(db: Session, plant_id: int) -> PlantReadWithPlanting:
    statement = select(Plant).where(Plant.id == plant_id)
    # db_plant = db.get(Plant, plant_id)
    results = db.exec(statement)
    return results # db_plant # db.query(Plant).filter(Plant.id == plant_id).first()


def get_plants(db: Session) -> List[PlantReadWithPlanting]:
    statement = select(Plant)
    results = db.exec(statement)
    return results


def create_plant(db: Session, _plant: PlantCreate | dict) -> PlantRead:
    """Add a plant to the database if it does not currently exist."""
    if isinstance(_plant, PlantCreate) or isinstance(_plant, Plant):
        plant = Plant.from_orm(_plant)
    elif isinstance(_plant, dict):
        plant = Plant(**_plant)
    db_plants = get_plants(db)
    if any(x.name_common == plant.name_common and x.variety == plant.variety \
           for x in db_plants):
        return None
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


def create_plants(db:Session, plants: list) -> List[PlantRead]:
    """Add a list of plants to the database"""
    for plant in plants:
        create_plant(db, plant)
    return get_plants(db)
