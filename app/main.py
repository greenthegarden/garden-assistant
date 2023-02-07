# import external modules

import json
from fastapi import Depends, FastAPI, Form, HTTPException, Header, Path, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select

from typing import Any, List, Optional

# import local modules

from app.database import engine, create_db_and_tables
from app.library.helpers import *
from app.models import Bed, BedCreate, BedRead, BedUpdate, Planting, PlantingCreate, PlantingRead, PlantingUpdate, Bed

# instantiate the FastAPI app
app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# See https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/
def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def index(request: Request,
          hx_request: Optional[str] = Header(None),
          ):
    plantings = [
        {'plant': 'cucumber', 'variety': 'lebanese', 'notes': ''}
    ]
    context = {"request": request, "plantings": plantings}
    if hx_request:
        return templates.TemplateResponse("table.html", context)
    return templates.TemplateResponse("index.html", context)


@app.get("/bed/add", response_class=HTMLResponse)
def beds_add(request: Request):
    context = {"request": request}
    return templates.TemplateResponse('beds/partials/add_bed_form.html', context)


@app.get("/beds/", response_class=HTMLResponse)
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
@app.post("/beds/", response_class=HTMLResponse)
def post_bed_create_form(request: Request,
                         session: Session = Depends(get_session),
                         name: str = Form(...),
                         soil_type: str = Form(...),
                         irrigation_zone: str = Form(...),
                         form_data: BedCreate = Depends(BedCreate.as_form)
                         ):
  print(f"name: {name}")
  print(f"soil_type: {soil_type}")
  print(f"irrigation_zone: {irrigation_zone}")
  print(f"Form data: {form_data}")
  # create_bed(bed=form_data)
  db_bed = Bed.from_orm(form_data)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  stmt = select(Bed)
  db_beds = session.exec(stmt).all()
  beds_data = jsonable_encoder(db_beds)
  print(beds_data)
  context = {"request": request, "beds": beds_data}
  return templates.TemplateResponse("beds/beds.html", context)


@app.get("/plantings/", response_class=HTMLResponse)
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
    

@app.post("/api/plantings/", response_model=PlantingRead)
def create_planting(*,
                    session: Session = Depends(get_session),
                    planting: PlantingCreate
                    ):
    db_planting = Planting.from_orm(planting)
    session.add(db_planting)
    session.commit()
    session.refresh(db_planting)
    return db_planting


@app.get("/api/plantings/", response_model=List[PlantingRead])
def read_plantings(*,
                   session: Session = Depends(get_session),
                   offset: int = 0,
                   limit: int = Query(default=100, lte=100)
                   ):
    # select * from
    stmt = select(Planting).offset(offset).limit(limit)
    db_plantings = session.exec(stmt).all()
    return db_plantings


@app.get("/api/plantings/{planting_id}", response_model=PlantingRead)
def read_planting(*,
                  session: Session = Depends(get_session),
                  planting_id: int = Path(None, description="The ID of the planting  to return")):
    # find the planting with the given ID, or None if it does not exist
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
        raise HTTPException(status_code=404, detail="Planting not found")
    return db_planting



@app.patch("/api/plantings/{planting_id}", response_model=PlantingRead)
def update_planting(*,
                    session: Session = Depends(get_session),
                    planting_id: int,
                    planting: PlantingUpdate,
                    ):
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
        raise HTTPException(status_code=404, detail="Planting not found")
    # update the planting data
    planting_data = planting.dict(exclude_unset=True)
    for key, val in planting_data.items():
        setattr(db_planting, key, val)
    session.add(db_planting)
    session.commit()
    session.refresh(db_planting)
    return db_planting


@app.delete("/api/plantings/{planting_id}")
def delete_planting(*,
                    session: Session = Depends(get_session),
                    planting_id: int,
                    ):
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
        raise HTTPException(status_code=404, detail="Planting not found")
    session.delete(db_planting)
    session.commit()
    return {"ok": True}


@app.post("/api/beds/", response_model=BedRead)
def create_bed(*,
               session: Session = Depends(get_session),
               bed: BedCreate
               ):
  print(f"Bed: {bed}")
  db_bed = Bed.from_orm(bed)
  session.add(db_bed)
  session.commit()
  session.refresh(db_bed)
  return db_bed


@app.get("/api/beds/", response_model=List[BedRead])
def read_beds(*,
              session: Session = Depends(get_session),
              offset: int = 0,
              limit: int = Query(default=100, lte=100)
              ):
    # select * from
    stmt = select(Bed).offset(offset).limit(limit)
    db_beds = session.exec(stmt).all()
    return db_beds


@app.get("/api/beds/{bed_id}", response_model=BedRead)
def read_bed(*, session: Session = Depends(get_session), bed_id: int):
    # find the planting with the given ID, or None if it does not exist
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return db_bed



@app.patch("/api/beds/{bed_id}", response_model=BedRead)
def update_bed(*,
               session: Session = Depends(get_session),
               bed_id: int,
               bed: BedUpdate,
               ):
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    # update the planting data
    bed_data = bed.dict(exclude_unset=True)
    for key, val in bed_data.items():
        setattr(db_bed, key, val)
    session.add(db_bed)
    session.commit()
    session.refresh(db_bed)
    return db_bed


@app.delete("/api/beds/{bed_id}")
def delete_bed(*,
               session: Session = Depends(get_session),
               bed_id: int,
               ):
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    session.delete(db_bed)
    session.commit()
    return {"ok": True}


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
