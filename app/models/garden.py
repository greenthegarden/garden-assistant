from enum import Enum as Enum_
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.library.form import as_form
if TYPE_CHECKING:
    from app.models.bed import Bed


# Class to return list of enum values
class Enum(Enum_):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class GardenType(str, Enum):
    SUBURBAN = "Suburban"
    ALLOTMENT = "Allotment"
    VERGE = "Verge"
    COMMUNITY = "Community"
    SMALL_HOLDING = "Small Holding"
    PATIO = "Patio"
    BALCONY = "Balcony"
    INDOOR = "Indoor"
    GREENHOUSE = "Greenhouse"


class ClimaticZone(str, Enum):
    ARID = "Arid"
    SUBTROPICAL = "Subtropical"
    TROPICAL = "Tropical"
    TEMPERATE = "Temperate"
    COOL = "Cool"


class GardenBase(SQLModel):
    name: str = Field(index=True)
    type: Optional[GardenType] = None
    location: Optional[str] = None
    zone: Optional[ClimaticZone] = None


class Garden(GardenBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beds: List["Bed"] = Relationship(back_populates="garden")


@as_form
class GardenCreate(GardenBase):
    pass


class GardenRead(GardenBase):
    id: int


class GardenUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[GardenType] = None
    location: Optional[str] = None
    zone: Optional[ClimaticZone] = None
