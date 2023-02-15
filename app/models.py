from datetime import datetime
from enum import Enum
from fastapi import Form
from fastapi_restful.enums import StrEnum
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional


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
  soil_type: Optional[SoilType]
  irrigation_zone: Optional[IrrigationZone]


class Bed(BedBase, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  plantings: List["Planting"] = Relationship(back_populates="bed")


class BedCreate(BedBase):
  pass

  @classmethod
  def as_form(
    cls,
    name: str = Form(...),
    soil_type: str = Form(...),
    irrigation_zone: str = Form(...)
  ):
    return cls(
      name=name,
      soil_type=soil_type,
      irrigation_zone=irrigation_zone
    )


class BedRead(BedBase):
  id: int
  
  
class BedUpdate(SQLModel):
  name: Optional[str] = None
  soil_type: Optional[str] = None
  irrigation_zone: Optional[str] = None


class PlantingBase(SQLModel):
  # name: str = Field(index=True)
  plant: str
  variety: Optional[str]
  # date_first_harvested: Optional[datetime]
  # date_removed: Optional[datetime]
  notes: Optional[str]
  bed_id: Optional[int] = Field(default=None, foreign_key="bed.id")
  
  
class Planting(PlantingBase, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  # date_planted: Optional[datetime] = Field(
  #   sa_column=Column(DateTime(timezone=True), server_default=func.now())
  #   )
  bed: Optional[Bed] = Relationship(back_populates="plantings")


class PlantingCreate(PlantingBase):
  pass


class PlantingRead(PlantingBase):
  id: int
  # date_planted: datetime

  
class PlantingUpdate(SQLModel):
  plant: Optional[str]
  variety: Optional[str]
  # date_planted: Optional[datetime]
  # date_first_harvested: Optional[datetime]
  # date_removed: Optional[datetime]
  notes: Optional[str]
  bed_id: Optional[int]
