import logging
from typing import List

from fastapi import (APIRouter, Depends, HTTPException, Query, Request,
                     Response, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..database.session import get_session
# from ..library.helpers import *
from ..library.routers import TimedRoute
from ..models.bed import Bed, BedCreate, BedRead, BedUpdate
from ..models.bed import IrrigationZone, SoilType
from ..models.garden import Garden
from ..models.relationships import BedReadWithGarden

logger = logging.getLogger(__name__)


bed_router = APIRouter(route_class=TimedRoute)
templates = Jinja2Templates(directory="templates")


# CRUD API methods for Garden Beds

@bed_router.post(
    "/api/beds/",
    status_code=status.HTTP_201_CREATED,
    response_model=BedRead,
    tags=["Garden Beds API"],
)
def create_bed(
    *,
    session: Session = Depends(get_session),
    response: Response,
    # user: User = Depends(auth_handler.get_current_user),
    bed: BedCreate,
):
    """Create a garden bed."""
    # if not user.gardener:
    #     response.status_code = status.HTTP_401_UNAUTHORIZED
    #     return {}
    statement = select(Bed)
    db_beds = session.exec(statement).all()
    if any(x.name == bed.name for x in db_beds):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bed with name {bed.name} already exists",
        )
    print(f"Bed: {bed}")
    db_bed = Bed.from_orm(bed)
    session.add(db_bed)
    session.commit()
    session.refresh(db_bed)
    return db_bed


@bed_router.get(
    "/api/beds/",
    response_model=List[BedRead],
    tags=["Garden Beds API"]
)
def read_beds(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """Get the list of defined garden beds."""
    statement = select(Bed).offset(offset).limit(limit)
    db_beds = session.exec(statement).all()
    return db_beds


@bed_router.get(
    "/api/beds/{bed_id}",
    response_model=BedReadWithGarden,
    tags=["Garden Beds API"]
)
def read_bed(
    *,
    session: Session = Depends(get_session),
    bed_id: int
):
    """Get the garden bed with the given ID, or None if it does not exist."""
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Bed with ID {bed_id} not found"
        )
    return db_bed


@bed_router.patch(
    "/api/beds/{bed_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=BedRead,
    tags=["Garden Beds API"],
)
def update_bed(
    *,
    session: Session = Depends(get_session),
    response: Response,
    # user: User = Depends(auth_handler.get_current_user),
    bed_id: int,
    bed: BedUpdate,
):
    """Update the details of the garden bed with the given ID."""
    # if not user.gardener:
    #     response.status_code = status.HTTP_401_UNAUTHORIZED
    #     return {}
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Bed with ID {bed_id} not found"
        )
    bed_data = bed.dict(exclude_unset=True)
    for key, val in bed_data.items():
        setattr(db_bed, key, val)
    session.add(db_bed)
    session.commit()
    session.refresh(db_bed)
    content = {"bed": jsonable_encoder(db_bed)}
    headers = {"HX-Trigger": "bedsChanged"}
    return JSONResponse(
        content=content,
        status_code=status.HTTP_201_CREATED,
        headers=headers
    )


@bed_router.delete(
    "/api/beds/{bed_id}",
    response_model=None,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Garden Beds API"],
)
def delete_bed(
    *,
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Bed with ID {bed_id} not found"
        )
    session.delete(db_bed)
    session.commit()
    content = {}
    headers = {"HX-Trigger": "bedsChanged"}
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
        headers=headers
    )


@bed_router.get(
    "/api/beds/soil_types/",
    response_model=List[SoilType],
    tags=["Garden Beds API"]
)
def read_soil_types():
    """Get the list of defined soil types."""
    soil_types = SoilType.list()
    print(soil_types)
    return soil_types


@bed_router.get(
    "/api/beds/irrigation_zones/",
    response_model=List[IrrigationZone],
    tags=["Garden Beds API"],
)
def read_irrigation_zones():
    """Get the list of defined irrigation zones."""
    irrigation_zones = IrrigationZone.list()
    print(irrigation_zones)
    return irrigation_zones


@bed_router.get(
    "/beds/",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def beds(request: Request):
    """Send content for beds page."""
    context = {"request": request}
    return templates.TemplateResponse("beds/beds.html", context)


@bed_router.get(
    "/beds/update",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def beds_update(
    request: Request,
    session: Session = Depends(get_session)
):
    """Update table contents for garden beds."""
    stmt = select(Bed)
    db_beds = session.exec(stmt).all()
    context = {
        "request": request,
        "beds": db_beds
    }
    return templates.TemplateResponse(
        "beds/partials/beds_table_body.html",
        context
    )


@bed_router.get(
    "/bed/create",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def bed_create_form(
    request: Request,
    session: Session = Depends(get_session)
):
    """Send model form to create a garden bed."""
    statement = select(Garden)
    db_gardens = session.exec(statement).all()
    irrigation_zones = IrrigationZone.list()
    soil_types = SoilType.list()
    context = {
        "request": request,
        "gardens": db_gardens,
        "irrigation_zones": irrigation_zones,
        "soil_types": soil_types,
    }
    return templates.TemplateResponse(
        "beds/partials/modal_form.html",
        context
    )


@bed_router.post(
    "/bed/create",
    response_class=JSONResponse,
    tags=["Pages API"]
)
def bed_create(
    session: Session = Depends(get_session),
    form_data: BedCreate = Depends(BedCreate.as_form),
):
    """Process form contents to create a garden bed."""
    db_bed = Bed.from_orm(form_data)
    session.add(db_bed)
    session.commit()
    session.refresh(db_bed)
    headers = {"HX-Trigger": "bedsChanged"}
    content = {"bed": jsonable_encoder(db_bed)}
    return JSONResponse(
        content=content,
        headers=headers
    )


@bed_router.get(
    "/bed/edit/{bed_id}",
    response_class=HTMLResponse,
    tags=["Pages API"]
)
def bed_edit_form(
    *,
    request: Request,
    session: Session = Depends(get_session),
    bed_id: int
):
    """Send modal form to edit a garden bed with the given ID."""
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Bed with ID {bed_id} not found"
        )
    statement = select(Garden)
    db_gardens = session.exec(statement).all()
    irrigation_zones = IrrigationZone.list()
    soil_types = SoilType.list()
    context = {
        "request": request,
        "bed": db_bed,
        "gardens": db_gardens,
        "irrigation_zones": irrigation_zones,
        "soil_types": soil_types,
    }
    return templates.TemplateResponse(
        "beds/partials/modal_form.html",
        context
    )


@bed_router.post(
    "/bed/edit/{bed_id}",
    response_class=JSONResponse,
    tags=["Pages API"]
)
async def bed_edit(
    request: Request,
    bed_id: int,
    session: Session = Depends(get_session)
):
    """Process form contents to update the details of the\
        garden bed with the given ID."""
    form = await request.form()
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Bed with ID {bed_id} not found"
        )
    for key, val in form.items():
        if val != "":
            setattr(db_bed, key, val)
    session.add(db_bed)
    session.commit()
    session.refresh(db_bed)
    content = {"bed": jsonable_encoder(db_bed)}
    headers = {"HX-Trigger": "bedsChanged"}
    return JSONResponse(
        content=content,
        headers=headers
    )
