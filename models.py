from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional


class BedBase(SQLModel):
  name: str = Field(index=True)
  soil_type: Optional[str]
  irrigation_zone: Optional[str]


class Bed(BedBase, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  plantings: List["Planting"] = Relationship(back_populates="bed")


class BedCreate(BedBase):
  pass


class BedRead(BedBase):
  id: int
  
  
class BedUpdate(SQLModel):
  name: Optional[str] = None
  soil_type: Optional[str] = None
  irrigation_zone: Optional[str] = None


class PlantingBase(SQLModel):
  name: str = Field(index=True)
  plant: str
  variety: Optional[str]
  # date_planted: Optional[datetime]
  # date_first_harvested: Optional[datetime]
  # date_removed: Optional[datetime]
  notes: Optional[str]
  bed_id: Optional[int] = Field(default=None, foreign_key="bed.id")
  
  
class Planting(PlantingBase, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  # date_planted: datetime
  bed: Optional[Bed] = Relationship(back_populates="plantings")

class PlantingCreate(PlantingBase):
  pass

class PlantingRead(PlantingBase):
  id: int
  
class PlantingUpdate(SQLModel):
  plant: Optional[str]
  variety: Optional[str]
  # date_planted: Optional[datetime]
  # date_first_harvested: Optional[datetime]
  # date_removed: Optional[datetime]
  notes: Optional[str]
  bed_id: Optional[int]
