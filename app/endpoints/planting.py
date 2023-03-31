# import external modules

import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List

# import local modules

from app.database.session import get_session
from app.library.helpers import *
from app.library.routers import TimedRoute
from app.models.garden_models import Bed
from app.models.garden_models import Planting, PlantingCreate, PlantingRead, PlantingUpdate
from app.models.user_models import User
from app.endpoints.api_user import auth_handler


logger = logging.getLogger(__name__)

                                      
planting_router = APIRouter(route_class=TimedRoute)
templates = Jinja2Templates(directory="templates")


# CRUD API methods for Garden Plantings

@planting_router.post("/api/plantings/", response_model=PlantingRead, status_code=status.HTTP_201_CREATED, tags=["Garden Plantings API"])
def create_planting(*,
                    session: Session = Depends(get_session),
                    planting: PlantingCreate
                    ):
  """Create a garden planting."""
  db_planting = Planting.from_orm(planting)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  return db_planting


@planting_router.get("/api/plantings/", response_model=List[PlantingRead], tags=["Garden Plantings API"])
def read_plantings(*,
                   session: Session = Depends(get_session),
                   offset: int = 0,
                   limit: int = Query(default=100, lte=100)
                   ):
  """Get the list of defined garden plantings."""
  stmt = select(Planting).offset(offset).limit(limit)
  db_plantings = session.exec(stmt).all()
  return db_plantings


@planting_router.get("/api/plantings/{planting_id}", response_model=PlantingRead, tags=["Garden Plantings API"])
def read_planting(*,
                  session: Session = Depends(get_session),
                  planting_id: int = Path(title="The ID of the planting to return")
                  ):
  """Get the garden planting with the given ID, or None if it does not exist."""
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=404, detail="Planting not found")
  return db_planting


@planting_router.patch("/api/plantings/{planting_id}", response_model=None, status_code=status.HTTP_201_CREATED, tags=["Garden Plantings API"])
def update_planting(*,
                    session: Session = Depends(get_session),
                    planting_id: int,
                    planting: PlantingUpdate,
                    ):
  """Update the details of the garden planting with the given ID."""
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planting not found")
  # update the planting data
  print(planting)
  planting_data = planting.dict(exclude_unset=True)
  print(planting_data)
  for key, val in planting_data.items():
    setattr(db_planting, key, val)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  content = {"planting": jsonable_encoder(db_planting)}
  headers = {"HX-Trigger": "plantingsChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_201_CREATED, headers=headers)


@planting_router.delete("/api/plantings/{planting_id}", response_model=None, status_code=status.HTTP_202_ACCEPTED, tags=["Garden Plantings API"])
def delete_planting(*,
                    session: Session = Depends(get_session),
                    planting_id: int,
                    ):
  """Delete the garden planting with the given ID."""
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planting not found")
  session.delete(db_planting)
  session.commit()
  content = {}
  headers = {"HX-Trigger": "plantingsChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_200_OK, headers=headers)

@planting_router.get("/plantings/", response_class=HTMLResponse, tags=["Pages API"])
def plantings(request: Request):
  """Send content for plantings page."""
  context = {"request": request}
  return templates.TemplateResponse("plantings/plantings.html", context)


@planting_router.get("/plantings/update", response_class=HTMLResponse, tags=["Pages API"])
def plantings_update(request: Request, session: Session = Depends(get_session)):
  """Update table contents for garden plantings."""
  statement = select(Planting)
  db_plantings = session.exec(statement).all()
  context = {"request": request, "plantings": db_plantings }
  return templates.TemplateResponse('plantings/partials/plantings_table_body.html', context)


@planting_router.get("/planting/create", response_class=HTMLResponse, tags=["Pages API"])
def planting_create_form(request: Request, session: Session = Depends(get_session)):
  """Send modal form to create a garden planting."""
  statement = select(Bed)
  db_beds = session.exec(statement).all()
  context = {"request": request, "beds": db_beds }
  return templates.TemplateResponse('plantings/partials/modal_form.html', context)


@planting_router.post("/planting/create", response_class=JSONResponse, tags=["Pages API"])
def planting_create(session: Session = Depends(get_session), form_data: PlantingCreate = Depends(PlantingCreate.as_form)):
  """Process form contents to create a garden planting."""
  db_planting = Planting.from_orm(form_data)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  headers = {"HX-Trigger": "plantingsChanged"}
  content = {"planting": jsonable_encoder(db_planting)}
  return JSONResponse(content=content, headers=headers)


@planting_router.get("/planting/edit/{planting_id}", response_class=HTMLResponse, tags=["Pages API"])
def planting_edit_form(*, request: Request, session: Session = Depends(get_session), planting_id: int):
  """Send modal form to update a garden planting with the given ID."""
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Planting not found')
  statement = select(Bed)
  db_beds = session.exec(statement).all()
  context = {"request": request, "planting": db_planting, "beds": db_beds }
  return templates.TemplateResponse('plantings/partials/modal_form.html', context)


# @planting_router.post("/planting/edit/{planting_id}", response_class=JSONResponse, tags=["Pages API"])
# async def planting_edit(request: Request, planting_id: int, session: Session = Depends(get_session)):
#   """Process form contents to update the details of the garden planting with the given ID."""
#   form = await request.form()
#   db_planting = session.get(Planting, planting_id)
#   if not db_planting:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Planting with ID {planting_id} not found')
#   for key, val in form.items():
#     if val != '':
#       setattr(db_planting, key, val)
#   session.add(db_planting)
#   session.commit()
#   session.refresh(db_planting)
#   content = {"planting": jsonable_encoder(db_planting)}
#   headers = {"HX-Trigger": "plantingsChanged"}
#   return JSONResponse(content=content, headers=headers)


@planting_router.post("/planting/edit/{planting_id}", response_class=JSONResponse, tags=["Pages API"])
async def planting_edit(request: Request, planting_id: int, form_data: PlantingUpdate = Depends(PlantingUpdate.as_form), session: Session = Depends(get_session)):
  """Process form contents to update the details of the garden planting with the given ID."""
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Planting with ID {planting_id} not found')
  print(form_data)
  planting_data = form_data.dict(exclude_unset=True)
  print(planting_data)
  for key, val in planting_data.items():
    setattr(db_planting, key, val)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  content = {"planting": jsonable_encoder(db_planting)}
  headers = {"HX-Trigger": "plantingsChanged"}
  return JSONResponse(content=content, headers=headers)
