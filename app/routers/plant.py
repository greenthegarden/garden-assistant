# import external modules

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_pagination import Page, paginate
from jinja2 import Template
from sqlmodel import Session, select
from typing import List


from fastapi_pagination import LimitOffsetPage, Page
from fastapi_pagination.ext.sqlmodel import paginate

# import local modules

from app.database.session import get_session
from app.library.helpers import *
from app.library.routers import TimedRoute
from app.models.plant import Plant, PlantRead, PlantCreate, PlantUpdate
from app.models.user import User
from app.routers.api_user import auth_handler
from app.routers.pages import templates


logger = logging.getLogger(__name__)


plant_router = APIRouter(route_class=TimedRoute)

plant_data = [
    {"name_common": "Amaranth",
    "name_botanical": "Amaranthus sp.",
    "family_group": "Amaranthaceae",
    "harvest": "12 to 16 weeks from seed.",
    "hints": "To make planting easier, mix tiny seeds with compost or sand before sowing.",
    "watch_for": "Can become weedy if let go to seed. Low germination rates are common.",
    "proven_varieties": "Golden"
    }
]

# CRUD API methods for Plants

@plant_router.post(
    "/api/plants/",
    status_code=status.HTTP_201_CREATED,
    response_model=PlantRead,
    tags=["Plant API"]
)
def create_plant(
    *,
    session: Session = Depends(get_session),
    response: Response,
    # user: User = Depends(auth_handler.get_current_user),
    plant: PlantCreate
):
    """Create a plant."""
    # if not user.gardener:
    #   response.status_code = status.HTTP_401_UNAUTHORIZED
    #   return {}
    statement = select(Plant)
    db_plants = session.exec(statement).all()
    if any(x.name == plant.name for x in db_plants):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plant with name {plant.name} already exists"
        )
    db_plant = Plant.from_orm(plant)
    session.add(db_plant)
    session.commit()
    session.refresh(db_plant)
    return db_plant


@plant_router.get(
        "/api/plants/",
        response_model=Page[PlantRead],
        tags=["Plant API"]
)
def read_plants(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100)
):
    """Get the list of defined plants."""
    statement = select(Plant).offset(offset).limit(limit)
    # db_plants = session.exec(statement).all()
    return paginate(session, statement)


@plant_router.get(
        "/api/plants/{plant_id}",
        response_model=PlantRead,
        tags=["Plant API"]
)
def read_plant(
    *,
    session: Session = Depends(get_session),
    plant_id: int
):
    """Get the plant with the given ID, or None if it does not exist."""
    db_plant = session.get(Plant, plant_id)
    if not db_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found"
        )
    return db_plant


@plant_router.patch(
        "/api/plants/{plant_id}",
        status_code=status.HTTP_201_CREATED,
        response_model=PlantRead,
        tags=["Plant API"]
)
def update_plant(
    *,
    session: Session = Depends(get_session),
    # user: User = Depends(auth_handler.get_current_user),
    plant_id: int,
    plant: PlantUpdate,
):
    """Update the details of the plant bed with the given ID."""
    # if not user.planter:
    #   response.status_code = status.HTTP_401_UNAUTHORIZED
    #   return {}
    db_plant = session.get(Plant, plant_id)
    if not db_plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Plant with ID {plant_id} not found')
    plant_data = plant.dict(exclude_unset=True)
    for key, val in plant_data.items():
        setattr(db_plant, key, val)
    session.add(db_plant)
    session.commit()
    session.refresh(db_plant)
    content = {"plant": jsonable_encoder(db_plant)}
    headers = {"HX-Trigger": "plantsChanged"}
    return JSONResponse(content=content, status_code=status.HTTP_201_CREATED, headers=headers)


@plant_router.delete("/api/plants/{plant_id}", response_model=None, status_code=status.HTTP_202_ACCEPTED, tags=["Plant API"])
def delete_plant(*, session: Session = Depends(get_session), plant_id: int):
    """Delete the plant with the given ID."""
    #  user: User = Depends(auth_handler.get_current_user),
    # if not user.planter:
    #   response.status_code = status.HTTP_401_UNAUTHORIZED
    #   return {}
    db_plant = session.get(Plant, plant_id)
    if not db_plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Plant with ID {plant_id} not found')
    session.delete(db_plant)
    session.commit()
    content = {}
    headers = {"HX-Trigger": "plantsChanged"}
    return JSONResponse(content=content, status_code=status.HTTP_200_OK, headers=headers)


@plant_router.get("/plants/", response_class=HTMLResponse, tags=["Plant API"])
def plants(request: Request):
    """Send content for plants page."""
    context = {"request": request}
    return templates.TemplateResponse("plants/plants.html", context)


@plant_router.get("/plants/update", response_class=HTMLResponse, tags=["Plant API"])
def plants_update(request: Request, session: Session = Depends(get_session)):
    """Update table contents for plants."""
    statement = select(Plant)
    db_plants = session.exec(statement).all()
    context = {"request": request, "plants": db_plants }
    return templates.TemplateResponse('plants/partials/plants_table_body.html', context)


@plant_router.get("/plant/create", response_class=HTMLResponse, tags=["Plant API"])
def plant_create_form(request: Request):
    """Send modal form to create a plant bed"""
    context = {"request": request }
    return templates.TemplateResponse('plants/partials/modal_form.html', context)


@plant_router.post("/plant/create", response_class=JSONResponse, tags=["Plant API"])
async def plant_create(session: Session = Depends(get_session), form_data: PlantCreate = Depends(PlantCreate.as_form)):
    """Process form contents to create a plant."""
    db_plant = Plant.from_orm(form_data)
    session.add(db_plant)
    session.commit()
    session.refresh(db_plant)
    headers = {"HX-Trigger": "plantsChanged"}
    content = {"planting": jsonable_encoder(db_plant)}
    return JSONResponse(content=content, headers=headers)


@plant_router.get("/plant/edit/{plant_id}", response_class=HTMLResponse, tags=["Plant API"])
def plant_edit_form(request: Request, plant_id: int, session: Session = Depends(get_session)):
    """Send modal form to update the plant with the given ID."""
    db_plant = session.get(Plant, plant_id)
    if not db_plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='plant not found')
    context = {"request": request, "plant": db_plant }
    return templates.TemplateResponse('plants/partials/modal_form.html', context)


@plant_router.post("/plant/edit/{plant_id}", response_class=JSONResponse, tags=["Plant API"])
async def plant_edit(request: Request, plant_id: int, session: Session = Depends(get_session)):
    """Process form contents to update the details of the plant with the given ID."""
    form = await request.form()
    db_plant = session.get(Plant, plant_id)
    if not db_plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'plant with ID {plant_id} not found')
    for key, val in form.items():
        if val != '':
            setattr(db_plant, key, val)
    session.add(db_plant)
    session.commit()
    session.refresh(db_plant)
    content = {"plant": jsonable_encoder(db_plant)}
    headers = {"HX-Trigger": "plantsChanged"}
    return JSONResponse(content=content, headers=headers)
