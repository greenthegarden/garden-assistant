import logging
import logging.config
from functools import lru_cache

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination


from .config import AppConfig, config
from .database.database import create_db_and_tables
from .library.metrics import metrics_app, all_requests
from .library.routers import TimedRoute
from .routers.api_user import user_router
from .routers.bed import bed_router
from .routers.garden import garden_router
from .routers.pages import pages_router
from .routers.plant import plant_router
from .routers.planting import planting_router
from .populate import populate_plants


# Logging setup based on https://philstories.medium.com/fastapi-logging-f6237b84ea64
# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
# the __name__ resolve to "main" since we are at the root of the project.
# This will get the root logger since no logger in the configuration has this name.
logger = logging.getLogger(__name__)   


@lru_cache()
def get_config():
    """_summary_

    Returns:
        _type_: _description_
    """
    return config


# instantiate the FastAPI app
app = FastAPI(title="Garden Assistant", debug=True)

router = APIRouter(route_class=TimedRoute)

@router.get("/info")
async def info(_config: AppConfig = Depends(get_config)):
    """Return settings defined in .env file

    Args:
        settings (Settings, optional): Get settings defined within .env file. \
            Defaults to Depends(get_settings).

    Returns:
        dict: parameters defined in .env
    """
    return {
        "app_name": _config.app_name,
        "admin_email": _config.admin_email,
        "items_per_user": _config.items_per_user,
    }

app.include_router(router)

app.include_router(garden_router)
app.include_router(bed_router)
app.include_router(planting_router)
app.include_router(plant_router)
app.include_router(user_router)
app.include_router(pages_router)

add_pagination(app)

app.mount("/metrics", metrics_app)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("tracing")
def tracing(request: Request, call_next):
    all_requests.inc()
    response = call_next(request)
    return response


@app.on_event("startup")
def on_startup():
    """Tasks run on application startup.
    """
    print("Creating database and tables...")
    create_db_and_tables()
    print("Populating tables...")
    populate_plants()
