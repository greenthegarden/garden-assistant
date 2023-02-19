# import external modules

import logging
from fastapi import APIRouter, Depends, HTTPException, Form, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

# import local modules

from app.database.session import get_session
from app.library.routers import TimedRoute
from app.models.garden_models import ClimaticZone, GardenType
from app.models.garden_models import IrrigationZone, SoilType
from app.models.garden_models import Garden, GardenCreate, GardenRead, GardenUpdate
from app.models.garden_models import Bed, BedCreate, BedRead, BedUpdate
from app.models.garden_models import Planting, PlantingCreate, PlantingRead, PlantingUpdate


logger = logging.getLogger(__name__)


# pages_router = APIRouter(route_class=TimedRoute)
pages_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@pages_router.get("/", response_class=HTMLResponse, tags=["Pages API"])
def index(request: Request, session: Session = Depends(get_session)):
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


@pages_router.get("/gardens/", response_class=HTMLResponse, tags=["Pages API"])
def gardens(request: Request):
  """Send content for gardens page."""
  context = {"request": request}
  return templates.TemplateResponse("gardens/gardens.html", context)


@pages_router.get("/gardens/update", response_class=HTMLResponse, tags=["Pages API"])
def gardens_update(request: Request, session: Session = Depends(get_session)):
  """Update table contents for gardens."""
  statement = select(Garden)
  db_gardens = session.exec(statement).all()
  context = {"request": request, "gardens": db_gardens }
  return templates.TemplateResponse('gardens/partials/gardens_table_body.html', context)


@pages_router.get("/garden/create", response_class=HTMLResponse, tags=["Pages API"])
def garden_create_form(request: Request):
  """Send modal form to create a garden bed"""
  types = GardenType.list()
  zones = ClimaticZone.list()
  context = {"request": request, "types": types, "zones": zones }
  return templates.TemplateResponse('gardens/partials/modal_form.html', context)


@pages_router.post("/garden/create", response_class=JSONResponse, tags=["Pages API"])
async def garden_create(request: Request, session: Session = Depends(get_session)):
  """Process form contents to create a garden."""
  errors = []
  try:
    form = await request.form()
    garden_name: str = str(form.get("name"))
    garden_type: str = str(form.get("type"))
    garden_zone: str = str(form.get("zone"))
    garden = GardenCreate(name=garden_name, type=garden_type, zone=garden_zone)
    db_garden = Garden.from_orm(garden)
    session.add(db_garden)
    session.commit()
    session.refresh(db_garden)
    content = {"garden": jsonable_encoder(db_garden)}
    headers = {"HX-Trigger": "gardensChanged"}
    return JSONResponse(content=content, headers=headers)
  except ValueError:
    print("In exception")
    errors.append("something went wrong! Ensure that Year and id are integers")
    content = {"request": request, "errors": errors}
    return JSONResponse(content=content)


@pages_router.get("/garden/edit/{garden_id}", response_class=HTMLResponse, tags=["Pages API"])
def garden_edit_form(request: Request, garden_id: int, session: Session = Depends(get_session)):
  """Send modal form to edit the garden with the given ID."""
  db_garden = session.get(Garden, garden_id)
  if not db_garden:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Garden not found')
  types = GardenType.list()
  zones = ClimaticZone.list()
  context = {"request": request, "garden": db_garden, "types": types, "zones": zones }
  return templates.TemplateResponse('gardens/partials/modal_form.html', context)


@pages_router.post("/garden/edit/{garden_id}", response_class=JSONResponse, tags=["Pages API"])
async def garden_edit(request: Request,
                      garden_id: int,
                      session: Session = Depends(get_session)):
  """Process form contents to edit a garden."""
  errors = []
  try:
    form = await request.form()
    garden_name: str = str(form.get("name"))
    garden_type: str = str(form.get("type"))
    garden_zone: str = str(form.get("zone"))
    garden = GardenUpdate(name=garden_name, type=garden_type, zone=garden_zone)
    db_garden = session.get(Garden, garden_id)
    if not db_garden:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Garden with ID {garden_id} not found')
    garden_data = garden.dict(exclude_unset=True)
    for key, val in garden_data.items():
      setattr(db_garden, key, val)
    session.add(db_garden)
    session.commit()
    session.refresh(db_garden)
    content = {"garden": jsonable_encoder(db_garden)}
    headers = {"HX-Trigger": "gardensChanged"}
    return JSONResponse(content=content, headers=headers)
  except ValueError:
    print("In exception")
    errors.append("something went wrong! Ensure that Year and id are integers")
    content = {"request": request, "errors": errors}
    return JSONResponse(content=content)
  
  
@pages_router.get("/beds/", response_class=HTMLResponse, tags=["Pages API"])
def beds(request: Request):
  """Send content for beds page."""
  context = {"request": request}
  return templates.TemplateResponse("beds/beds.html", context)


@pages_router.get("/beds/update", response_class=HTMLResponse, tags=["Pages API"])
def beds_update(request: Request, session: Session = Depends(get_session)):
  """Update table contents for garden beds."""
  stmt = select(Bed)
  db_beds = session.exec(stmt).all()
  context = {"request": request, "beds": db_beds }
  return templates.TemplateResponse('beds/partials/beds_table_body.html', context)


@pages_router.get("/bed/create", response_class=HTMLResponse, tags=["Pages API"])
def bed_create_form(request: Request, session: Session = Depends(get_session)):
  """Send modal form to create a garden bed."""
  statement = select(Garden)
  db_gardens = session.exec(statement).all()
  irrigation_zones = IrrigationZone.list()
  soil_types = SoilType.list()
  context = {"request": request, "gardens": db_gardens, "irrigation_zones": irrigation_zones, "soil_types": soil_types }
  return templates.TemplateResponse('beds/partials/modal_form.html', context)


@pages_router.post("/bed/create", response_class=JSONResponse, tags=["Pages API"])
def bed_create(session: Session = Depends(get_session), form_data: BedCreate = Depends(BedCreate.as_form)):
  """Process form contents to create a garden bed."""
  db_bed = Bed.from_orm(form_data)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  headers = {"HX-Trigger": "bedsChanged"}
  content = {"bed": jsonable_encoder(db_bed)}
  return JSONResponse(content=content, headers=headers)


@pages_router.get("/bed/edit/{bed_id}", response_class=HTMLResponse, tags=["Pages API"])
def bed_edit_form(*, request: Request, session: Session = Depends(get_session), bed_id: int):
  """Send modal form to edit a garden bed with the given ID."""
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Bed not found')
  statement = select(Garden)
  db_gardens = session.exec(statement).all()
  irrigation_zones = IrrigationZone.list()
  soil_types = SoilType.list()
  context = {"request": request, "bed": db_bed, "gardens": db_gardens, "irrigation_zones": irrigation_zones, "soil_types": soil_types }
  return templates.TemplateResponse('beds/partials/modal_form.html', context)


@pages_router.post("/bed/edit/{bed_id}", response_class=JSONResponse, tags=["Pages API"])
def post_bed_edit_form(request: Request,
                         bed_id: int,
                         session: Session = Depends(get_session),
                         name: str = Form(...),
                         soil_type: str = Form(...),
                         irrigation_zone: str = Form(...),
                         ) -> dict:
  """Process form contents to update the details of the garden bed with the given ID."""
  print(f"name: {name}")
  print(f"soil_type: {soil_type}")
  print(f"irrigation_zone: {irrigation_zone}")
  db_bed = session.get(Bed, bed_id)
  if not db_bed:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bed with ID {bed_id} not found")
  # update the bed data
  bed_data = bed.dict(exclude_unset=True)
  for key, val in planting_data.items():
    setattr(db_planting, key, val)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  content = {db_planting}
  headers = {"HX-Trigger": "plantingsChanged"}
  return JSONResponse(content=content, status_code=status.HTTP_201_CREATED, headers=headers)


@pages_router.get("/plantings/", response_class=HTMLResponse, tags=["Pages API"])
def plantings(request: Request):
  """Send content for plantings page."""
  context = {"request": request}
  return templates.TemplateResponse("plantings/plantings.html", context)


@pages_router.get("/plantings/update", response_class=HTMLResponse, tags=["Pages API"])
def plantings_update(request: Request, session: Session = Depends(get_session)):
  """Update table contents for garden plantings."""
  statement = select(Planting)
  db_plantings = session.exec(statement).all()
  context = {"request": request, "plantings": db_plantings }
  return templates.TemplateResponse('plantings/partials/plantings_table_body.html', context)


@pages_router.get("/planting/create", response_class=HTMLResponse, tags=["Pages API"])
def planting_create_form(request: Request, session: Session = Depends(get_session)):
  """Send modal form to create a garden planting"""
  statement = select(Bed)
  db_beds = session.exec(statement).all()
  context = {"request": request, "beds": db_beds }
  return templates.TemplateResponse('plantings/partials/modal_form.html', context)


@pages_router.post("/planting/create", response_class=JSONResponse, tags=["Pages API"])
def planting_create(session: Session = Depends(get_session), form_data: PlantingCreate = Depends(PlantingCreate.as_form)):
  """Process form contents to create a garden planting."""
  db_planting = Planting.from_orm(form_data)
  session.add(db_planting)
  session.commit()
  session.refresh(db_planting)
  headers = {"HX-Trigger": "plantingsChanged"}
  content = {"planting": jsonable_encoder(db_planting)}
  return JSONResponse(content=content, headers=headers)


@pages_router.get("/planting/edit/{planting_id}", response_class=HTMLResponse, tags=["Pages API"])
def planting_edit_form(*, request: Request, session: Session = Depends(get_session), planting_id: int):
  """Send modal form to edit a garden planting with the given ID."""
  db_planting = session.get(Planting, planting_id)
  if not db_planting:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Planting not found')
  statement = select(Bed)
  db_beds = session.exec(statement).all()
  context = {"request": request, "planting": db_planting, "beds": db_beds }
  return templates.TemplateResponse('plantings/partials/modal_form.html', context)


@pages_router.post("/planting/edit/{planting_id}", response_class=JSONResponse, tags=["Pages API"])
async def planting_edit(request: Request,
                         planting_id: int,
                         session: Session = Depends(get_session)):
  """Process form contents to edit the details of the garden planting with the given ID."""
  errors = []
  try:
    form = await request.form()
    planting_plant: str = str(form.get("plant"))
    planting_variety: str = str(form.get("variety"))
    planting_bed_id: int = int(form.get("bed_id"))
    planting = PlantingUpdate(plant=planting_plant, variety=planting_variety, bed_id=planting_bed_id)
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Planting with ID {planting_id} not found')
    planting_data = planting.dict(exclude_unset=True)
    for key, val in planting_data.items():
      setattr(db_planting, key, val)
    session.add(db_planting)
    session.commit()
    session.refresh(db_planting)
    content = {"planting": jsonable_encoder(db_planting)}
    headers = {"HX-Trigger": "plantingsChanged"}
    return JSONResponse(content=content, headers=headers)
  except ValueError:
    print("In exception")
    errors.append("something went wrong! Ensure that Year and id are integers")
    content = {"request": request, "errors": errors}
    return JSONResponse(content=content)
