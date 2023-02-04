# import external modules

from fastapi import Depends, FastAPI, HTTPException, Header, Query, Request
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


# See https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/
def get_session():
    with Session(engine) as session:
        yield session


@app.post("/plantings/", response_model=PlantingRead)
def create_planting(*,
                    session: Session = Depends(get_session),
                    planting: PlantingCreate
                    ):
    db_planting = Planting.from_orm(planting)
    session.add(db_planting)
    session.commit()
    session.refresh(db_planting)
    return db_planting


@app.get("/plantings/", response_model=List[PlantingRead])
def read_plantings(*,
                   session: Session = Depends(get_session),
                   offset: int = 0,
                   limit: int = Query(default=100, lte=100)
                   ):
    # select * from
    stmt = select(Planting).offset(offset).limit(limit)
    db_plantings = session.exec(stmt).all()
    return db_plantings


@app.get("/plantings/{planting_id}", response_model=PlantingRead)
def read_planting(*, session: Session = Depends(get_session), planting_id: int):
    # find the planting with the given ID, or None if it does not exist
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
        raise HTTPException(status_code=404, detail="Planting not found")
    return db_planting



@app.patch("/plantings/{planting_id}", response_model=PlantingRead)
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


@app.delete("/plantings/{planting_id}")
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


@app.post("/beds/", response_model=BedRead)
def create_bed(*,
               session: Session = Depends(get_session),
               bed: BedCreate
               ):
    db_bed = Bed.from_orm(bed)
    session.add(db_bed)
    session.commit()
    session.refresh(db_bed)
    return db_bed


@app.get("/beds/", response_model=List[BedRead])
def read_beds(*,
              session: Session = Depends(get_session),
              offset: int = 0,
              limit: int = Query(default=100, lte=100)
              ):
    # select * from
    stmt = select(Bed).offset(offset).limit(limit)
    db_beds = session.exec(stmt).all()
    return db_beds


@app.get("/beds/{bed_id}", response_model=BedRead)
def read_bed(*, session: Session = Depends(get_session), bed_id: int):
    # find the planting with the given ID, or None if it does not exist
    db_bed = session.get(Bed, bed_id)
    if not db_bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return db_bed



@app.patch("/beds/{bed_id}", response_model=BedRead)
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


@app.delete("/beds/{bed_id}")
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
