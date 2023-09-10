# import external modules

import logging

from functools import lru_cache

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles

from fastapi_pagination import Page, paginate, add_pagination
from fastapi_sqlalchemy import DBSessionMiddleware, db

import os
from dotenv import load_dotenv


# Logging setup based on https://philstories.medium.com/fastapi-logging-f6237b84ea64
# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)  # the __name__ resolve to "main" since we are at the root of the project. 
                                      # This will get the root logger since no logger in the configuration has this name.

# Ensure environment is defined
from app.config import Settings

load_dotenv('.env')

# Load configuration
from app.configurator import config

import uvicorn

# import local modules

# from app.database.database import create_db_and_tables
from app.library.routers import TimedRoute
from app.endpoints.garden import garden_router
from app.endpoints.bed import bed_router
from app.endpoints.planting import planting_router
from app.endpoints.plant import plant_router
from app.endpoints.pages import pages_router
from app.endpoints.api_user import user_router
# from app.populate import create_planting_db


# instantiate the FastAPI app
app = FastAPI(title="Garden Assistant", debug=True)
add_pagination(app)

router = APIRouter(route_class=TimedRoute)

app.include_router(garden_router)
app.include_router(bed_router)
app.include_router(planting_router)
app.include_router(plant_router)
app.include_router(user_router)
app.include_router(pages_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


# https://www.educative.io/answers/how-to-use-postgresql-database-in-fastapi
# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#     logger.info(f"rid={idem} start request path={request.url.path}")
#     start_time = time.time()
    
#     response = await call_next(request)
    
#     process_time = (time.time() - start_time) * 1000
#     formatted_process_time = '{0:.2f}'.format(process_time)
#     logger.debug(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
    
#     return response


# @lru_cache()
# def get_settings():
#     return Settings()


@router.get("/info")
async def info(config: Settings = Depends(config)):
    return {
        "app_name": config.app_name,
        "items_per_user": config.items_per_user,
    }

app.include_router(router)

@app.on_event("startup")
def on_startup():
  print(f"Creating database and tables...")
  create_db_and_tables()
  # print(f"Populating tables...")  
  # create_planting_db()


def main():
  print(f"Creating database and tables...")
  create_db_and_tables()
  # print(f"Populating tables...")  
  # create_planting_db()


# To run locally
if __name__ == "__main__":
  
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
