import os.path
from sqlmodel import SQLModel, create_engine

# There should be one engine for the entire application
sqlite_filename = 'db.sqlite3'
sqlite_file = os.path.join("./", sqlite_filename)
sqlite_url = f"sqlite:///{sqlite_file}"

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    """Create the tables registered with SQLModel.metadata (i.e classes with table=True).
    More info: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#sqlmodel-metadata
    """
    SQLModel.metadata.create_all(engine)
