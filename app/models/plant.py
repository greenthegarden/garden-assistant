from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from ..library.form import as_form
from .planting import Planting


# Model based on https://www.abc.net.au/gardening/plant-finder
class PlantBase(SQLModel):
    """Base model for a plant.

    The common name and variety are both required and indexed to be\
    able to search for plants effeciently.
    """
    name_common: str = Field(index=True)
    variety: str = Field(index=True)
    name_botanical: Optional[str] = None
    family_group: Optional[str] = None
    harvest: Optional[str]= None
    hints: Optional[str] = None
    watch_for: Optional[str] = None
    proven_varieties: Optional[str] = None

    planting_id: Optional[int] = Field(default=None, foreign_key="planting.id")


class Plant(PlantBase, table=True):
    """Plant model with relationship to associated planting."""
    id: Optional[int] = Field(default=None, primary_key=True)

    planting: Optional[Planting] = Relationship(back_populates="plants")


@as_form
class PlantCreate(PlantBase):
    """Plant model used to create instances of plants."""
    pass


class PlantRead(PlantBase):
    """Plant model used to get instances of plants."""
    id: int


class PlantUpdate(SQLModel):
    """Plant model used to update instances of plants."""
    name_common: Optional[str] = None
    variety: Optional[str] = None
    name_botanical: Optional[str] = None
    family_group: Optional[str] = None
    harvest: Optional[str] = None
    hints: Optional[str] = None
    watch_for: Optional[str] = None
    proven_varieties: Optional[str] = None
    planting: Optional[Planting] = None
