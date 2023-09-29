import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database.session import get_session
from app.library.helpers import *
from app.library.routers import TimedRoute
from app.models.bed import Bed
from app.models.garden import ClimaticZone, GardenType
from app.models.garden import Garden, GardenCreate, GardenRead, GardenUpdate
from app.models.user import User
from app.routers.api_user import auth_handler


logger = logging.getLogger(__name__)


garden_router = APIRouter(route_class=TimedRoute)
templates = Jinja2Templates(directory="templates")


# CRUD API methods for Garden

@garden_router.post(
    "/api/gardens/",
    status_code=status.HTTP_201_CREATED,
    response_model=GardenRead,
    tags=["Garden API"]
)
def create_garden(
    *,
    session: Session = Depends(get_session),
    response: Response,
    # user: User = Depends(auth_handler.get_current_user),
    garden: GardenCreate,
) -> GardenRead:
    """Create a garden."""
    # if not user.gardener:
    #   response.status_code = status.HTTP_401_UNAUTHORIZED
    #   return {}
    statement = select(Garden)
    db_gardens = session.exec(statement).all()
    if any(x.name == garden.name for x in db_gardens):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Garden with name {garden.name} already exists"
        )
    db_garden = Garden.from_orm(garden)
    session.add(db_garden)
    session.commit()
    session.refresh(db_garden)
    return db_garden


@garden_router.get(
    "/api/gardens/",
    response_model=List[GardenRead],
    tags=["Garden API"])
def read_gardens(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100)
):
    """Get the list of defined gardens."""
    statement = select(Garden).offset(offset).limit(limit)
    db_gardens = session.exec(statement).all()
    return db_gardens


@garden_router.get(
    "/api/gardens/{garden_id}",
    response_model=GardenRead,
    tags=["Garden API"]
)
def read_garden(
    *,
    session: Session = Depends(get_session),
    garden_id: int
):
    """Get the garden with the given ID, or None if it does not exist."""
    db_garden = session.get(Garden, garden_id)
    if not db_garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Garden with ID {garden_id} not found'
        )
    return db_garden


@garden_router.patch(
    "/api/gardens/{garden_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=GardenRead,
    tags=["Garden API"]
)
def update_garden(
    *,
    session: Session = Depends(get_session),
    response: Response,
    #  user: User = Depends(auth_handler.get_current_user),
    garden_id: int,
    garden: GardenUpdate,
):
    """Update the details of the garden bed with the given ID."""
    # if not user.gardener:
    #     response.status_code = status.HTTP_401_UNAUTHORIZED
    #     return {}
    db_garden = session.get(Garden, garden_id)
    if not db_garden:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Garden with ID {garden_id} not found'
        )
    garden_data = garden.dict(exclude_unset=True)
    for key, val in garden_data.items():
        setattr(db_garden, key, val)
    session.add(db_garden)
    session.commit()
    session.refresh(db_garden)
    content = {"garden": jsonable_encoder(db_garden)}
    headers = {"HX-Trigger": "gardensChanged"}
    return JSONResponse(
        content=content,
        status_code=status.HTTP_201_CREATED,
        headers=headers
    )


@garden_router.delete(
    "/api/gardens/{garden_id}",
    response_model=None,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Garden API"]
)
def delete_garden(
    *,
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Garden with ID {garden_id} not found'
        )
    session.delete(db_garden)
    session.commit()
    content = {}
    headers = {"HX-Trigger": "gardensChanged"}
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
        headers=headers
    )


@garden_router.get(
    "/gardens/",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def gardens(request: Request):
    """Send content for gardens page."""
    context = {"request": request}
    return templates.TemplateResponse(
        "gardens/gardens.html",
        context
    )


@garden_router.get(
    "/gardens/update",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def gardens_update(
    request: Request,
    session: Session = Depends(get_session)
):
    """Update table contents for gardens."""
    statement = select(Garden)
    db_gardens = session.exec(statement).all()
    context = {"request": request, "gardens": db_gardens }
    return templates.TemplateResponse(
        "gardens/partials/gardens_table_body.html",
        context
    )


@garden_router.get(
    "/garden/create",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def garden_create_form(request: Request):
    """Send modal form to create a garden bed"""
    types = GardenType.list()
    zones = ClimaticZone.list()
    context = {
        "request": request,
        "types": types,
        "zones": zones
    }
    return templates.TemplateResponse(
        "gardens/partials/modal_form.html",
        context
    )


@garden_router.post(
    "/garden/create",
    response_class=JSONResponse,
    tags=["Pages API"]
)
async def garden_create(
    session: Session = Depends(get_session),
    form_data: GardenCreate = Depends(GardenCreate.as_form)
):
    """Process form contents to create a garden."""
    db_garden = Garden.from_orm(form_data)
    session.add(db_garden)
    session.commit()
    session.refresh(db_garden)
    headers = {"HX-Trigger": "gardensChanged"}
    content = {"garden": jsonable_encoder(db_garden)}
    return JSONResponse(
        content=content,
        headers=headers
    )


@garden_router.get(
    "/garden/edit/{garden_id}",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def garden_edit_form(
    request: Request,
    garden_id: int,
    session: Session = Depends(get_session)
):
    """Send modal form to update the garden with the given ID."""
    db_garden = session.get(Garden, garden_id)
    if not db_garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Garden not found'
    )
    types = GardenType.list()
    zones = ClimaticZone.list()
    context = {
        "request": request,
        "garden": db_garden,
        "types": types,
        "zones": zones
    }
    return templates.TemplateResponse(
        'gardens/partials/modal_form.html',
        context
    )


@garden_router.post(
    "/garden/edit/{garden_id}",
    response_class=JSONResponse,
    tags=["Pages API"]
)
async def garden_edit(
    request: Request,
    garden_id: int,
    session: Session = Depends(get_session)
):
    """Process form contents to update the details of the garden with the given ID."""
    form = await request.form()
    db_garden = session.get(Garden, garden_id)
    if not db_garden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Garden with ID {garden_id} not found'
        )
    for key, val in form.items():
        if val != '':
            setattr(db_garden, key, val)
    session.add(db_garden)
    session.commit()
    session.refresh(db_garden)
    content = {"garden": jsonable_encoder(db_garden)}
    headers = {"HX-Trigger": "gardensChanged"}
    return JSONResponse(
        content=content,
        headers=headers
    )
