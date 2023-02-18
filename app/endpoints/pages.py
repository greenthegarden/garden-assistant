# import external modules

import logging
from fastapi import APIRouter, Depends, Form, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

# import local modules

from app.database.session import get_session
from app.library.routers import TimedRoute
from app.models.garden_models import IrrigationZone, SoilType
from app.models.garden_models import Bed, BedCreate, BedRead, BedUpdate
from app.models.garden_models import Planting, PlantingCreate, PlantingRead, PlantingUpdate


logger = logging.getLogger(__name__)


pages_router = APIRouter(route_class=TimedRoute)
templates = Jinja2Templates(directory="templates")


@pages_router.get("/", response_class=HTMLResponse, tags=["Pages API"])
def index(request: Request,
          session: Session = Depends(get_session),
          ):
  statement = select(Bed)
  db_beds = session.exec(statement).all()
  bed_exists = False
  if len(db_beds) > 0:
    bed_exists = True
  statement = select(Planting)
  db_plantings = session.exec(statement).all()
  planting_exists = False
  if len(db_plantings) > 0:
    planting_exists = True
  context = {"request": request, "bed_exists": bed_exists, "planting_exists": planting_exists}
  return templates.TemplateResponse("index.html", context)


@pages_router.get("/beds/", response_class=HTMLResponse, tags=["Pages API"])
def beds(request: Request):
  """Send content for beds page"""
  context = {"request": request}
  return templates.TemplateResponse("beds/beds.html", context)


@pages_router.get("/beds/update", response_class=HTMLResponse, tags=["Pages API"])
def beds_update(request: Request, session: Session = Depends(get_session)):
  """Update table contents for garden beds"""
  stmt = select(Bed)
  db_beds = session.exec(stmt).all()
  context = {"request": request, "beds": db_beds }
  return templates.TemplateResponse('beds/partials/beds_table_body.html', context)


@pages_router.get("/bed/form", response_class=HTMLResponse, tags=["Pages API"])
def bed_form(request: Request):
  """Send modal form to create a garden bed"""
  irrigation_zones = IrrigationZone.list()
  soil_types = SoilType.list()
  context = {"request": request, "irrigation_zones": irrigation_zones, "soil_types": soil_types }
  return templates.TemplateResponse('beds/partials/modal_form.html', context)


@pages_router.post("/beds/", response_class=JSONResponse, tags=["Pages API"])
def post_bed_create_form(request: Request,
                         session: Session = Depends(get_session),
                         name: str = Form(...),
                         soil_type: str = Form(...),
                         irrigation_zone: str = Form(...),
                         form_data: BedCreate = Depends(BedCreate.as_form)
                         ):
  """Process form contents to create a garden bed"""
  print(f"name: {name}")
  print(f"soil_type: {soil_type}")
  print(f"irrigation_zone: {irrigation_zone}")
  print(f"Form data: {form_data}")
  # create_bed(bed=form_data)
  print(request)
  db_bed = Bed.from_orm(form_data)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  headers = {"HX-Trigger": "bedsChanged"}
  content = {"bed": jsonable_encoder(db_bed)}
  return JSONResponse(content=content, headers=headers)


@pages_router.get("/plantings/", response_class=HTMLResponse, tags=["Pages API"])
def plantings(request: Request):
  """Send content for plantings page"""
  context = {"request": request}
  return templates.TemplateResponse("plantings/plantings.html", context)


@pages_router.get("/plantings/update", response_class=HTMLResponse, tags=["Pages API"])
def plantings_update(request: Request, session: Session = Depends(get_session)):
  """Update table contents for garden plantings"""
  stmt = select(Planting)
  db_plantings = session.exec(stmt).all()
  context = {"request": request, "plantings": db_plantings }
  return templates.TemplateResponse('plantings/partials/plantings_table_body.html', context)


@pages_router.get("/planting/form", response_class=HTMLResponse, tags=["Pages API"])
def planting_form(request: Request, session: Session = Depends(get_session)):
  """Send modal form to create a garden planting"""
  stmt = select(Bed)
  db_beds = session.exec(stmt).all()
  context = {"request": request, "beds": db_beds }
  return templates.TemplateResponse('plantings/partials/modal_form.html', context)


# Get a form and process contents to create a garden bed
@pages_router.post("/plantings/", response_class=JSONResponse, tags=["Pages API"])
def planting_create_from_form(request: Request,
                         session: Session = Depends(get_session),
                         plant: str = Form(...),
                         variety: str = Form(...),
                         bed: str = Form(...),
                         notes: str = Form(...),
                         form_data: PlantingCreate = Depends(PlantingCreate.as_form)
                         ):
  """Process form contents to create a garden planting"""
  print(f"plant: {plant}")
  print(f"variety: {variety}")
  print(f"bed: {bed}")
  print(f"notes: {notes}")
  print(f"Form data: {form_data}")
  # create_bed(bed=form_data)
  print(request)
  db_planting = Planting.from_orm(form_data)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  headers = {"HX-Trigger": "plantingsChanged"}
  content = {"planting": jsonable_encoder(db_planting)}
  return JSONResponse(content=content, headers=headers)
