"""Reusable CRUD functions to interact with the data in the database.

Based on https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

# from sqlalchemy.orm import Session
from sqlmodel import Session, select

from ..models.garden import Garden, GardenCreate
from ..models.plant import Plant, PlantCreate


# def get_garden(db: Session, garden_id: int):
#     return db.query(Garden).filter(Garden.id == garden_id).first()


# # def get_user_by_email(db: Session, email: str):
# #     return db.query(models.User).filter(models.User.email == email).first()


# def get_gardens_all(db: Session, offset: int = 0, limit: Query(default=100, lte=100)):
#     statement = select(Garden).offset(offset).limit(limit)
#     return db.session.exec(statement).all()


# def create_garden(db: Session, user: GardenCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_garden = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item


def get_plant(db: Session, plant_id: int):
    return db.query(Plant).filter(Plant.id == plant).first()




def get_plants(db: Session):
    return db.query(Plant).all()



def create_plant(db: Session, plant: PlantCreate):
    db_plants = get_plants(db)
    if any(x.name_common == plant.name_common and x.variety == plant.variety \
           for x in db_plants):
        raise Exception()
    db_plant = PlantCreate(**plant.dict())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant
