import uvicorn


def run(host, port):
    """Launch with `poetry run start` at root level
    """
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
    