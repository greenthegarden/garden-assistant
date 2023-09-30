from typing import List, Optional, TYPE_CHECKING

from fastapi import Form
from sqlmodel import Field, Relationship, SQLModel

from ..library.form import as_form
from .bed import Bed
if TYPE_CHECKING:
    from .plant import Plant


class PlantingBase(SQLModel):
    """Base model for a planting"""
    name: str = Field(index=True)
    # date_first_harvested: Optional[datetime]
    # date_removed: Optional[datetime]
    notes: Optional[str] = None

    bed_id: Optional[int] = Field(default=None, foreign_key="bed.id")


class Planting(PlantingBase, table=True):
    """Planting model with relationship to associated garden bed and plants."""
    id: Optional[int] = Field(default=None, primary_key=True)

    bed: Optional[Bed] = Relationship(back_populates="plantings")
    plants: List["Plant"] = Relationship(back_populates="planting")


@as_form
class PlantingCreate(PlantingBase):
    """Planting model used to create instances of plantings."""
    pass


class PlantingRead(PlantingBase):
    """Planting model used to get instances of plantings."""
    id: int
    # date_planted: datetime


class PlantingUpdate(SQLModel):
    """Planting model used to update instances of plantings."""
    name: Optional[str] = None
    # date_planted: Optional[datetime]
    # date_first_harvested: Optional[datetime]
    # date_removed: Optional[datetime]
    notes: Optional[str] = None
    bed_id: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        plant: Optional[str] = Form(...),
        variety: Optional[str] = Form(...),
        notes: Optional[str] = Form(...),
        bed_id: Optional[int] = Form(...),
    ):
        """Form to update instances of plantings"""
        return cls(plant=plant, variety=variety, notes=notes, bed_id=bed_id)
