"""Reusable CRUD functions to interact with the garden data in the database.

Based on https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

from sqlmodel import Session
from typing import List

from ..models.garden import Garden, GardenCreate, GardenRead


def get_garden(db: Session, garden_id: int) -> GardenRead:
    return db.query(Garden).filter(Garden.id == garden_id).first()


def get_gardens(db: Session) -> List[GardenRead]:
    return db.query(Garden).all()


def create_garden(db: Session, garden: GardenCreate | dict) -> GardenRead:
    db_gardens = get_gardens(db)
    if any(x.name == garden.name for x in db_gardens):
        return None
    if isinstance(garden, GardenCreate) or isinstance(garden, Garden):
        db_garden = Garden.from_orm(garden)
    elif isinstance(garden, dict):
        db_garden = Garden(**garden)
    db.add(db_garden)
    db.commit()
    db.refresh(db_garden)
    return db_garden
