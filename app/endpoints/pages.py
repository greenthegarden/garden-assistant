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
  stmt = select(Planting)
  db_plantings = session.exec(stmt).all()
  context = {"request": request, "plantings": db_plantings}
  return templates.TemplateResponse("index.html", context)


@pages_router.get("/bed/form", response_class=HTMLResponse, tags=["Pages API"])
def beds_form(request: Request):
  irrigation_zones = IrrigationZone.list()
  soil_types = SoilType.list()
  context = {"request": request, "irrigation_zones": irrigation_zones, "soil_types": soil_types }
  # return templates.TemplateResponse('beds/partials/add_bed_form.html', context)
  return templates.TemplateResponse('beds/partials/modal_form.html', context)


@pages_router.get("/beds/update", tags=["Pages API"])
def beds_update(request: Request,
                session: Session = Depends(get_session),
                ):
  stmt = select(Bed)
  db_beds = session.exec(stmt).all()
  context = {"request": request, "beds": db_beds }
  # return templates.TemplateResponse('beds/partials/add_bed_form.html', context)
  return templates.TemplateResponse('beds/partials/beds_table_body.html', context)


@pages_router.get("/beds/cancel_add", tags=["Pages API"])
def cancel_beds(request: Request):
    url = request.headers.get('HX-Current-URL')
    url_path = url.split('/')[-2]
    print(url_path)
    context = {"request": request}
    if url_path == 'beds':
        return templates.TemplateResponse('beds/partials/show_add_bed_form.html', context)
    return templates.TemplateResponse('plantings/partials/show_add_form.html', context)


@pages_router.get("/beds/", response_class=HTMLResponse, tags=["Pages API"])
def beds(request: Request,
         session: Session = Depends(get_session),
         ):
  stmt = select(Bed)
  db_beds = session.exec(stmt).all()
  beds_data = jsonable_encoder(db_beds)
  print(beds_data)
  # context for alpine.js
  # context = {"request": request, "beds": json.dumps(beds_data)}
  # context for htmx
  context = {"request": request, "beds": beds_data}
  return templates.TemplateResponse("beds/beds.html", context)


# Get a form and process contents to create a garden bed
@pages_router.post("/beds/", response_class=JSONResponse, tags=["Pages API"])
def post_bed_create_form(request: Request,
                         session: Session = Depends(get_session),
                         name: str = Form(...),
                         soil_type: str = Form(...),
                         irrigation_zone: str = Form(...),
                         form_data: BedCreate = Depends(BedCreate.as_form)
                         ):
  # async with request.form() as form:
  #   print(f"form: {form}")
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


@pages_router.get("/plantings/add", response_class=HTMLResponse, tags=["Pages API"])
def plantings_add(request: Request):
  context = {"request": request}
  return templates.TemplateResponse('plantings/partials/show_add_form.html', context)


@pages_router.get("/plantings/", response_class=HTMLResponse, tags=["Pages API"])
def plantings(request: Request,
              session: Session = Depends(get_session),
              ):
  stmt = select(Planting)
  results = session.exec(stmt).all()
  plantings_data = jsonable_encoder(results)
  # beds = set([p['Bed']['name'] for p in plantings_data])
  context = {"request": request,
              "plantings": plantings_data,
              }
  return templates.TemplateResponse("plantings/plantings.html", context)
