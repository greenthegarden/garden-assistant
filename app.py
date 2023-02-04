import json
import pathlib
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select

from database import engine, create_db_and_tables
from models import Planting, PlantingCreate, PlantingRead, PlantingUpdate

# instantiate the FastAPI app
app = FastAPI()

# create container for our data - to be loaded at app startup.
data = []


@app.on_event("startup")
async def startup_event():
    DATAFILE = pathlib.Path() / 'data' / 'plantings.json'
    session = Session(engine)
    # check if the database is already populated
    stmt = select(Planting)
    result = session.exec(stmt).first()

    # Load data if there are no results
    if result is None:
        with open(DATAFILE, 'r') as f:
            plantings = json.load(f)
            for planting in plantings:
                session.add(Planting(**planting))
        session.commit()
    session.close()


# See https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/
def get_session():
    with Session(engine) as session:
        yield session


@app.get('/plantings/', response_model=List[PlantingRead])
def plantings(offset: int = 0,
           limit: int = Query(default=100, lte=100),
           session: Session = Depends(get_session)):
    # select * from
    stmt = select(Planting).offset(offset).limit(limit)
    db_plantings = session.exec(stmt).all()
    return db_plantings


@app.get('/plantings/{planting_id}/', response_model=PlantingRead)
def planting(planting_id: int, session: Session = Depends(get_session)):
    # find the planting with the given ID, or None if it does not exist
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
        raise HTTPException(status_code=404, detail="Planting not found")
    return db_planting


@app.post("/plantings/", response_model=PlantingRead, status_code=201)
def create_planting(planting: PlantingCreate, session: Session = Depends(get_session)):
    db_planting = Planting.from_orm(planting)
    session.add(db_planting)
    session.commit()
    session.refresh(db_planting)
    return db_planting


@app.patch("/plantings/{planting_id}", response_model=PlantingRead)
def update_planting(planting_id: int,
                 planting: PlantingUpdate,
                 session: Session = Depends(get_session)):
    db_planting = session.get(Planting, planting_id)
    if not db_planting:
        raise HTTPException(status_code=404, detail="planting not found")
    # update the planting data
    planting_data = planting.dict(exclude_unset=True)
    for key, val in planting_data.items():
        setattr(db_planting, key, val)
    session.add(db_planting)
    session.commit()
    session.refresh(db_planting)
    return db_planting


@app.delete("/plantings/{planting_id}")
def delete_planting(planting_id: int,
                 session: Session = Depends(get_session)):
    db_plantings = session.get(Planting, planting_id)
    if not db_plantings:
        raise HTTPException(status_code=404, detail="planting not found")
    session.delete(db_plantings)
    session.commit()
    return {"ok": True}


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
