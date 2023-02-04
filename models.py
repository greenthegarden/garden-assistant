from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel

class PlantingBase(SQLModel):
  plant: str = Field(index=True)
  variety: Optional[str]
  # date_planted: Optional[datetime]
  # date_first_harvested: Optional[datetime]
  # date_removed: Optional[datetime]
  notes: Optional[str]
  
class Planting(PlantingBase, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  # date_planted: datetime

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
