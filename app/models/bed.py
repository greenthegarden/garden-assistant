from enum import Enum as Enum_
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from ..library.form import as_form
from .garden import Garden
if TYPE_CHECKING:
    from .planting import Planting


class Enum(Enum_):
    """Helper class to return list of enum values."""
    @classmethod
    def list(cls):
        """Returns list of enum values for the given class"""
        return list(map(lambda c: c.value, cls))


class SoilType(str, Enum):
    """Definition of a set of soil types"""
    LOAM = "Loam"
    CLAY = "Clay"
    SILT = "Silt"
    SAND = "Sand"
    POTTING_MIX = "Potting Mix"
    SEED_RAISING_MIX = "Seed Raising Mix"
    COMPOST = "Compost"


class IrrigationZone(str, Enum):
    """Definition of a set of irrigation zones"""
    GRASS = "Grass"
    TREES = "Trees"
    SHRUBS = "Shrubs"
    VEGETABLES = "Vegetables"


class BedBase(SQLModel):
    """Base model for a garden bed"""
    name: str = Field(index=True)
    soil_type: Optional[SoilType] = None
    irrigation_zone: Optional[IrrigationZone] = None

    garden_id: Optional[int] = Field(default=None, foreign_key="garden.id")


class Bed(BedBase, table=True):
    """Garden bed model with relationship to associated garden and plantings."""
    id: Optional[int] = Field(default=None, primary_key=True)

    garden: Optional[Garden] = Relationship(back_populates="beds")
    plantings: List["Planting"] = Relationship(back_populates="bed")


@as_form
class BedCreate(BedBase):
    """Garden bed model used to create instances of garden beds."""
    pass


class BedRead(BedBase):
    """Garden bed model used to get instances of garden beds."""
    id: int


class BedUpdate(SQLModel):
    """Garden bed model used to update instances of garden beds."""
    name: Optional[str] = None
    soil_type: Optional[SoilType] = None
    irrigation_zone: Optional[IrrigationZone] = None
