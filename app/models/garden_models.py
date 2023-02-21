from datetime import datetime
from enum import Enum as Enum_
from fastapi import Form
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional

from app.library.form import as_form


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


class PlantingBase(SQLModel):
  # name: str = Field(index=True)
  plant: str
  variety: Optional[str] = None
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


@as_form
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
  
  @classmethod
  def as_form(
    cls,
    plant: Optional[str] = Form(...),
    variety: Optional[str] = Form(...),
    notes: Optional[str] = Form(...),
    bed_id: Optional[int] = Form(...)
  ):
    return cls(
      plant=plant,
      variety=variety,
      notes=notes,
      bed_id=bed_id
    )
