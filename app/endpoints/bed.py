# import external modules

import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import List

# import local modules

from app.database.session import get_session
from app.library.helpers import *
from app.library.routers import TimedRoute
from app.models.garden_models import IrrigationZone, SoilType
from app.models.garden_models import Garden, GardenCreate, GardenRead, GardenUpdate
from app.models.garden_models import Bed, BedCreate, BedRead, BedUpdate
from app.models.garden_models import Planting, PlantingCreate, PlantingRead, PlantingUpdate
from app.models.user_models import User
from app.endpoints.api_user import auth_handler


logger = logging.getLogger(__name__)

                                      
bed_router = APIRouter(route_class=TimedRoute)


# CRUD API methods for Garden Beds

@bed_router.post("/api/beds/", status_code=status.HTTP_201_CREATED, response_model=BedRead, tags=["Garden Beds API"])
def create_bed(*,
               session: Session = Depends(get_session),
               response: Response,
               user: User = Depends(auth_handler.get_current_user),
               bed: BedCreate
               ):
  """Create a garden bed."""
  if not user.gardener:
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {}
  statement = select(Bed)
  db_beds = session.exec(statement).all()
  if any(x.name == bed.name for x in db_beds):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bed with name {bed.name} already exists")
  print(f"Bed: {bed}")
  db_bed = Bed.from_orm(bed)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  return db_bed


@bed_router.get("/api/beds/", response_model=List[BedRead], tags=["Garden Beds API"])
def read_beds(*,
              session: Session = Depends(get_session),
              offset: int = 0,
              limit: int = Query(default=100, lte=100)
              ):
  """Get the list of defined garden beds."""
  stmt = select(Bed).offset(offset).limit(limit)
  db_beds = session.exec(stmt).all()
  return db_beds


@bed_router.get("/api/beds/{bed_id}", response_model=BedRead, tags=["Garden Beds API"])
def read_bed(*, session: Session = Depends(get_session), bed_id: int):
  """Get the garden bed with the given ID, or None if it does not exist."""
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Bed not found')
  return db_bed


@bed_router.patch("/api/beds/{bed_id}", status_code=status.HTTP_201_CREATED, response_model=BedRead, tags=["Garden Beds API"])
def update_bed(*,
               session: Session = Depends(get_session),
               response: Response,
               user: User = Depends(auth_handler.get_current_user),
               bed_id: int,
               bed: BedUpdate,
               ):
  """Update the details of the garden bed with the given ID."""
  if not user.gardener:
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {}
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Bed not found')
  # update the planting data
  bed_data = bed.dict(exclude_unset=True)
  for key, val in bed_data.items():
    setattr(db_bed, key, val)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  content = {db_bed}
  headers = {"HX-Trigger": "bedsChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_201_CREATED, headers=headers)


@bed_router.delete("/api/beds/{bed_id}", response_model=None, status_code=status.HTTP_202_ACCEPTED, tags=["Garden Beds API"])
def delete_bed(*,
               session: Session = Depends(get_session),
               response: Response,
               bed_id: int,
               ):
  """Delete the garden bed with the given ID."""
              #  user: User = Depends(auth_handler.get_current_user),
  # if not user.gardener:
  #   response.status_code = status.HTTP_401_UNAUTHORIZED
  #   return {}
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Bed not found')
  session.delete(db_bed)
  session.commit()
  content = {}
  headers = {"HX-Trigger": "bedsChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_200_OK, headers=headers)


@bed_router.get("/api/beds/soil_types/", response_model=List[SoilType], tags=["Garden Beds API"])
def read_soil_types():
  """Get the list of defined soil types."""
  soil_types = SoilType.list()
  print(soil_types)
  return soil_types


@bed_router.get("/api/beds/irrigation_zones/", response_model=List[IrrigationZone], tags=["Garden Beds API"])
def read_irrigation_zones():
  """Get the list of defined irrigation zones."""
  irrigation_zones = IrrigationZone.list()
  print(irrigation_zones)
  return irrigation_zones
