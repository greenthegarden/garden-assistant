from typing import List, Optional, TYPE_CHECKING

from fastapi import Form
from sqlmodel import Field, Relationship, SQLModel

from ..library.form import as_form
from .bed import Bed
if TYPE_CHECKING:
    from .plant import Plant


class PlantingBase(SQLModel):
    # name: str = Field(index=True)
    plant: str
    # variety: Optional[str] = None
    # date_first_harvested: Optional[datetime]
    # date_removed: Optional[datetime]
    notes: Optional[str] = None
    bed_id: Optional[int] = Field(default=None, foreign_key="bed.id")


class Planting(PlantingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # date_planted: Optional[datetime] = Field(
    #   sa_column=Column(DateTime(timezone=True), server_default=func.now())
    #   )
    bed: Optional[Bed] = Relationship(back_populates="plantings")
    # plants: List["Plant"] = Relationship(back_populates="planting")


@as_form
class PlantingCreate(PlantingBase):
    pass


class PlantingRead(PlantingBase):
    id: int
    # date_planted: datetime


class PlantingUpdate(SQLModel):
    plant: Optional[str] = None
    variety: Optional[str] = None
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
        return cls(plant=plant, variety=variety, notes=notes, bed_id=bed_id)
