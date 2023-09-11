# Garden Assistant Development Notes

## Project References

| Link | Repository | Influenced |
| ---- | ---------- | ---------- |
| <https://medium.com/gitconnected/building-a-website-starter-with-fastapi-92d077092864> | | |
| <https://betterprogramming.pub/fastapi-best-practices-1f0deeba4fce> | | |
| [FastAPI - SQLModel Relationships and Alpine.js integration](https://www.youtube.com/watch?v=qlXJu2U1jc4) | | |
| <https://www.youtube.com/watch?v=mGU3j51waWA> | | |
| [Forms and File Uploads with FastAPI and Jinja2](https://www.youtube.com/watch?v=L4WBFRQB7Lk)
| [Reimagining front-end web development with htmx and hyperscript](https://nomadiq.hashnode.dev/reimagining-front-end-web-development-with-htmx-and-hyperscript) | | Frontend using HTMX and Hyperscript |
| [HTMX_FastAPI_Login](https://github.com/eddyizm/HTMX_FastAPI_Login) | https://github.com/eddyizm/HTMX_FastAPI_Login | User authentication |
| [How to Implement Pagination Using FastAPI in Python](https://medium.com/python-in-plain-english/how-to-implement-pagination-using-fastapi-in-python-6d57be902fd5) | Pagination |

## Project structure

Code structure updated to conform with <https://sqlmodel.tiangolo.com/tutorial/code-structure/>

## Creating venv

Information based on <https://docs.python.org/3/library/venv.html> and <https://python.land/virtual-environments/virtualenv>

```powershell
python3 -m venv C:\Users\cutle\Development\garden-assistant --upgrade-deps
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Scripts\Activate.ps1
```

```bash
python3 -m venv venv
source venv/bin/activate
```

## Poetry

Install Poetry using instructions from https://python-poetry.org/docs/#installation.

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

```bash
pipx install poetry
```

## Dependencies

* [FastAPI](https://fastapi.tiangolo.com/) as the web framework
* [SQLModel](https://sqlmodel.tiangolo.com/) as the SQL database abstraction layer
* [Alembic](https://alembic.sqlalchemy.org/en/latest/) for database versioning and migration

For production deployment install dependencies using

```sh
python -m pip install -r requirements/prod.txt
```

For development, to support running tests, install dependencies using

```sh
python -m pip install -r requirements/dev.txt
```

For poetry

```sh
poetry install
```

## VSCode

To ensure Pylance extension finds the correct modules, ensure the Python interpretor being used is set to `Scripts\python.exe`.


## Tests

To run tests use

```sh
pytest tests/test_main.py
```

## Server

Run the server using

```sh
uvicorn app.main:app --reload
```

Using poetry

```sh
poetry run start
```

## Database Migrations

[Alembic](https://alembic.sqlalchemy.org/en/latest/) is utilised to enable database migration.

To initialise use

```sh
alembic init migrations
```

Ensure import statements for `sqlmodel` ardded to both the `migrations/script.py.mako` and `migrations/env.py` files. In addition, ensure all models are imported into the `migrations/env.py` file

Update sqlalchemy url in `alembic.ini` file

To create the first migration use

```sh
alembic revision --autogenerate -m "initial migration"
```

## Docker Container Images

Create image

```sh
docker build -t garden-assistant .
```

Run container

```sh
docker run -d --name garden-assistant -p 80:80 garden-assistant
```
