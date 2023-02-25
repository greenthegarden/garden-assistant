# import external modules

import logging

from functools import lru_cache
import random
import string
import time

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles

import uvicorn

# import local modules

from app.config import Settings
from app.database.database import create_db_and_tables
from app.library.routers import TimedRoute
from app.endpoints.api_garden import garden_router
from app.endpoints.api_user import user_router
from app.endpoints.plant import plant_router
from app.endpoints.pages import pages_router
from app.populate import create_planting_db


# Logging setup based on https://philstories.medium.com/fastapi-logging-f6237b84ea64
# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)  # the __name__ resolve to "main" since we are at the root of the project. 
                                      # This will get the root logger since no logger in the configuration has this name.
                                      
# instantiate the FastAPI app
app = FastAPI()

router = APIRouter(route_class=TimedRoute)

app.include_router(garden_router)
app.include_router(plant_router)
app.include_router(user_router)
app.include_router(pages_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


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


@lru_cache()
def get_settings():
    return Settings()


@router.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_user": settings.items_per_user,
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


if __name__ == "__main__":
  # main()
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
