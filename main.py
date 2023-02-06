# import external modules

import json
from fastapi import Depends, FastAPI, HTTPException, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session, select

from typing import List, Optional

# import local modules

from database import engine, create_db_and_tables
from models import Bed, BedCreate, BedRead, BedUpdate, Planting, PlantingCreate, PlantingRead, PlantingUpdate, Bed

# instantiate the FastAPI app
app = FastAPI()

templates = Jinja2Templates(directory="templates")


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


@app.get("/beds/", response_class=HTMLResponse)
def beds(request: Request,
         session: Session = Depends(get_session),
         ):
    db_beds = session.exec(select(Bed))
    context = {"request": request, "beds": db_beds}
    return templates.TemplateResponse("beds.html", context)


@app.get("/plantings/", response_class=HTMLResponse)
def plantings(request: Request,
              session: Session = Depends(get_session),
              ):
    # db_plantings = session.exec(select(Planting))
    stmt = select(Planting, Bed).where(Planting.bed_id == Bed.id)
    results = session.exec(stmt).all()
    print(results[0])
    print(type(results))
    plantings_data = jsonable_encoder(results)
    beds = set([p['Bed']['name'] for p in plantings_data])
    print(plantings_data)
    print(type(plantings_data))
    context = {"request": request,
               "plantings": json.dumps(plantings_data),
               "beds": beds
               }
    print(json.dumps(plantings_data))
    print(type(json.dumps(plantings_data)))
    return templates.TemplateResponse("plantings.html", context)
    

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
def read_planting(*, session: Session = Depends(get_session), planting_id: int):
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
