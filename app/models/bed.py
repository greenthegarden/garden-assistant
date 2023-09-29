from enum import Enum as Enum_
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from ..library.form import as_form
from .garden import Garden
if TYPE_CHECKING:
    from .planting import Planting


# Class to return list of enum values
class Enum(Enum_):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class SoilType(str, Enum):
    LOAM = "Loam"
    CLAY = "Clay"
    SILT = "Silt"
    SAND = "Sand"
    POTTING_MIX = "Potting Mix"
    SEED_RAISING_MIX = "Seed Raising Mix"
    COMPOST = "Compost"


class IrrigationZone(str, Enum):
    GRASS = "Grass"
    TREES = "Trees"
    SHRUBS = "Shrubs"
    VEGETABLES = "Vegetables"


class BedBase(SQLModel):
    name: str = Field(index=True)
    soil_type: Optional[SoilType] = None
    irrigation_zone: Optional[IrrigationZone] = None
    garden_id: Optional[int] = Field(default=None, foreign_key="garden.id")


class Bed(BedBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    garden: Optional[Garden] = Relationship(back_populates="beds")
    plantings: List["Planting"] = Relationship(back_populates="bed")


@as_form
class BedCreate(BedBase):
    pass


class BedRead(BedBase):
    id: int


class BedUpdate(SQLModel):
    name: Optional[str] = None
    soil_type: Optional[SoilType] = None
    irrigation_zone: Optional[IrrigationZone] = None
