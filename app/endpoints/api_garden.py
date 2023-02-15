# import external modules

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, select
from typing import List

# import local modules

from app.database.session import get_session
from app.library.helpers import *
from app.models.garden_models import Bed, BedCreate, BedRead, BedUpdate
from app.models.garden_models import Planting, PlantingCreate, PlantingRead, PlantingUpdate


garden_router = APIRouter()


# CRUD API methods for Garden Beds

@garden_router.post("/api/beds/", response_model=BedRead)
def create_bed(*,
               session: Session = Depends(get_session),
               bed: BedCreate
               ):
  print(f"Bed: {bed}")
  db_bed = Bed.from_orm(bed)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  return db_bed


@garden_router.get("/api/beds/", response_model=List[BedRead])
def read_beds(*,
              session: Session = Depends(get_session),
              offset: int = 0,
              limit: int = Query(default=100, lte=100)
              ):
  # select * from
  stmt = select(Bed).offset(offset).limit(limit)
  db_beds = session.exec(stmt).all()
  return db_beds


@garden_router.get("/api/beds/{bed_id}", response_model=BedRead)
def read_bed(*, session: Session = Depends(get_session), bed_id: int):
  # find the planting with the given ID, or None if it does not exist
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=404, detail="Bed not found")
  return db_bed


@garden_router.patch("/api/beds/{bed_id}", response_model=BedRead)
def update_bed(*,
               session: Session = Depends(get_session),
               bed_id: int,
               bed: BedUpdate,
               ):
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=404, detail="Bed not found")
  # update the planting data
  bed_data = bed.dict(exclude_unset=True)
  for key, val in bed_data.items():
    setattr(db_bed, key, val)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  return db_bed


@garden_router.delete("/api/beds/{bed_id}")
def delete_bed(*,
               session: Session = Depends(get_session),
               bed_id: int,
               ):
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=404, detail="Bed not found")
  session.delete(db_bed)
  session.commit()
  return {"ok": True}


# CRUD API methods for Garden Plantings

@garden_router.post("/api/plantings/", response_model=PlantingRead)
def create_planting(*,
                    session: Session = Depends(get_session),
                    planting: PlantingCreate
                    ):
  db_planting = Planting.from_orm(planting)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  return db_planting


@garden_router.get("/api/plantings/", response_model=List[PlantingRead])
def read_plantings(*,
                   session: Session = Depends(get_session),
                   offset: int = 0,
                   limit: int = Query(default=100, lte=100)
                   ):
  # select * from
  stmt = select(Planting).offset(offset).limit(limit)
  db_plantings = session.exec(stmt).all()
  return db_plantings


@garden_router.get("/api/plantings/{planting_id}", response_model=PlantingRead)
def read_planting(*,
                  session: Session = Depends(get_session),
                  planting_id: int = Path(None, description="The ID of the planting  to return")):
  # find the planting with the given ID, or None if it does not exist
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=404, detail="Planting not found")
  return db_planting


@garden_router.patch("/api/plantings/{planting_id}", response_model=PlantingRead)
def update_planting(*,
                    session: Session = Depends(get_session),
                    planting_id: int,
                    planting: PlantingUpdate,
                    ):
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=404, detail="Planting not found")
  # update the planting data
  planting_data = planting.dict(exclude_unset=True)
  for key, val in planting_data.items():
    setattr(db_planting, key, val)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  return db_planting


@garden_router.delete("/api/plantings/{planting_id}")
def delete_planting(*,
                    session: Session = Depends(get_session),
                    planting_id: int,
                    ):
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=404, detail="Planting not found")
  session.delete(db_planting)
  session.commit()
  return {"ok": True}
