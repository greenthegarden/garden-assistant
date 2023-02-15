# import external modules

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import uvicorn

# import local modules

from app.database.database import create_db_and_tables
from app.endpoints.api_garden import garden_router
from app.endpoints.pages import pages_router
from app.populate import create_planting_db


# instantiate the FastAPI app
app = FastAPI()

app.include_router(garden_router)
app.include_router(pages_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
  print(f"Creating database and tables...")
  create_db_and_tables()
  print(f"Populating tables...")  
  create_planting_db()


def main():
  print(f"Creating database and tables...")
  create_db_and_tables()
  print(f"Populating tables...")  
  create_planting_db()


if __name__ == "__main__":
  main()
  uvicorn.run(app.main, host="127.0.0.1", port=8000)
