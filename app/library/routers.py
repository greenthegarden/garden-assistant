"""Module to create a custom route handler to monitor request"""
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute


# https://stackoverflow.com/questions/69670125/how-to-log-raw-http-request-response-in-python-fastapi/73464007#73464007
class TimedRoute(APIRoute):
    """Custom route handler with timer

    Args:
        APIRoute (_type_): Route to time
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler
