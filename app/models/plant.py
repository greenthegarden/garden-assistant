from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from ..library.form import as_form

# if TYPE_CHECKING:
#     from app.models.planting import Planting

# Model based on https://www.abc.net.au/gardening/plant-finder
class PlantBase(SQLModel):
    name_common: str = Field(index=True)
    name_botanical: Optional[str] = None
    family_group: Optional[str] = None
    harvest: Optional[str]= None
    hints: Optional[str] = None
    watch_for: Optional[str] = None
    proven_varieties: Optional[str] = None
    # planting_id: Optional[int] = Field(default=None, foreign_key="planting.id")


class Plant(PlantBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # planting: List["Planting"] = Relationship(back_populates="plants")


@as_form
class PlantCreate(PlantBase):
    pass


class PlantRead(PlantBase):
    id: int


class PlantUpdate(SQLModel):
    name_common: Optional[str] = None
    name_botanical: Optional[str] = None
    family_group: Optional[str] = None
    harvest: Optional[str] = None
    hints: Optional[str] = None
    watch_for: Optional[str] = None
    proven_varieties: Optional[str] = None
