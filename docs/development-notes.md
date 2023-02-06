# Garden Assistant Development Notes

## Project References

* <https://medium.com/gitconnected/building-a-website-starter-with-fastapi-92d077092864>
* <https://betterprogramming.pub/fastapi-best-practices-1f0deeba4fce>
* [FastAPI - SQLModel Relationships and Alpine.js integration](https://www.youtube.com/watch?v=qlXJu2U1jc4)
* <https://www.youtube.com/watch?v=mGU3j51waWA>
* [Forms and File Uploads with FastAPI and Jinja2](https://www.youtube.com/watch?v=L4WBFRQB7Lk)

## Dependencies

* [FastAPI](https://fastapi.tiangolo.com/) as the web framework
* [SQLModel](https://sqlmodel.tiangolo.com/) as the SQL database abstraction layer

For production deployment install dependencies using

```sh
pip install -r requirements/prod.txt
```

For development, to support running tests, install dependencies using

```sh
pip install -r requirements/dev.txt
```

## Project structure

Code structure updated to conform with <https://sqlmodel.tiangolo.com/tutorial/code-structure/>

## Creating venv

Information based on <https://docs.python.org/3/library/venv.html>

```powershell
python3 -m venv C:\Users\cutle\Development\garden-assistant --upgrade-deps
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Scripts\Activate.ps1
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
