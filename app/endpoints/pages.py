# import external modules

import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

# import local modules

from app.database.session import get_session
from app.models.garden_models import Garden
from app.models.garden_models import Bed
from app.models.garden_models import Planting


logger = logging.getLogger(__name__)


# pages_router = APIRouter(route_class=TimedRoute)
pages_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@pages_router.get("/", response_class=HTMLResponse, tags=["Pages API"])
def index(request: Request, session: Session = Depends(get_session)):
  statement = select(Garden)
  db_gardens = session.exec(statement).all()
  garden_exists = False
  if len(db_gardens) > 0:
    garden_exists = True
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
  context = {"request": request, "garden_exists": garden_exists, "bed_exists": bed_exists, "planting_exists": planting_exists}
  return templates.TemplateResponse("index.html", context)
