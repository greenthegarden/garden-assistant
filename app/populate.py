from sqlmodel import Session

from app.database.database import engine
from app.models.garden_models import IrrigationZone, SoilType
from app.models.garden_models import Bed, Planting


def create_bed():
  bed = Bed(name="Vegetable Plot",
            soil_type=SoilType.LOAM,
            irrigation_zone=IrrigationZone.VEGETABLES
           )
  return bed
  
  
def create_planting(bed: Bed):
  planting = Planting(plant="Tomato",
                      variety="Cherry",
                      notes="",
                      bed_id=bed.id
                      )
  return planting
  

def create_planting_db():
  bed = create_bed();
  print(bed)
  with Session(engine) as session:
    session.add(bed)
    session.commit()
    session.refresh(bed)
    planting = create_planting(bed)
    session.add(planting)
    session.commit()
    
    
# create_planting_db()
