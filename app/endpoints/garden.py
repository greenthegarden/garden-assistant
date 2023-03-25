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

                                      
garden_router = APIRouter(route_class=TimedRoute)


# CRUD API methods for Garden Beds

@garden_router.post("/api/gardens/", status_code=status.HTTP_201_CREATED, response_model=GardenRead, tags=["Garden API"])
def create_garden(*,
               session: Session = Depends(get_session),
               response: Response,
               user: User = Depends(auth_handler.get_current_user),
               garden: GardenCreate
               ):
  """Create a garden."""
  if not user.gardener:
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {}
  statement = select(Garden)
  db_gardens = session.exec(statement).all()
  if any(x.name == garden.name for x in db_gardens):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Garden with name {garden.name} already exists")
  db_garden = Bed.from_orm(garden)
  session.add(db_garden)
  session.commit()
  session.refresh(db_garden)
  return db_garden


@garden_router.get("/api/gardens/", response_model=List[GardenRead], tags=["Garden API"])
def read_gardens(*,
              session: Session = Depends(get_session),
              offset: int = 0,
              limit: int = Query(default=100, lte=100)
              ):
  """Get the list of defined gardens."""
  statement = select(Garden).offset(offset).limit(limit)
  db_gardens = session.exec(statement).all()
  return db_gardens


@garden_router.get("/api/gardens/{garden_id}", response_model=GardenRead, tags=["Garden API"])
def read_garden(*, session: Session = Depends(get_session), garden_id: int):
  """Get the garden with the given ID, or None if it does not exist."""
  db_garden = session.get(Garden, garden_id)
  if not db_garden:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Garden with ID {garden_id} not found')
  return db_garden


@garden_router.patch("/api/gardens/{garden_id}", status_code=status.HTTP_201_CREATED, response_model=GardenRead, tags=["Garden API"])
def update_garden(*,
               session: Session = Depends(get_session),
               response: Response,
               user: User = Depends(auth_handler.get_current_user),
               garden_id: int,
               garden: GardenUpdate,
               ):
  """Update the details of the garden bed with the given ID."""
  if not user.gardener:
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {}
  db_garden = session.get(Garden, garden_id)
  if not db_garden:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Garden with ID {garden_id} not found')
  # update the planting data
  garden_data = garden.dict(exclude_unset=True)
  for key, val in garden_data.items():
    setattr(db_garden, key, val)
  session.add(db_garden)
  session.commit()
  session.refresh(db_garden)
  content = {"garden": jsonable_encoder(db_garden)}
  headers = {"HX-Trigger": "gardensChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_201_CREATED, headers=headers)


@garden_router.delete("/api/gardens/{garden_id}", response_model=None, status_code=status.HTTP_202_ACCEPTED, tags=["Garden API"])
def delete_garden(*,
               session: Session = Depends(get_session),
               response: Response,
               garden_id: int,
               ):
  """Delete the garden with the given ID."""
              #  user: User = Depends(auth_handler.get_current_user),
  # if not user.gardener:
  #   response.status_code = status.HTTP_401_UNAUTHORIZED
  #   return {}
  db_garden = session.get(Garden, garden_id)
  if not db_garden:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Garden with ID {garden_id} not found')
  session.delete(db_garden)
  session.commit()
  content = {}
  headers = {"HX-Trigger": "gardensChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_200_OK, headers=headers)
