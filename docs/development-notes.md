# Garden Assistant Development Notes

## Dependencies

* [FastAPI](https://fastapi.tiangolo.com/) as the web framework
* [SQLModel](https://sqlmodel.tiangolo.com/) as the SQL database abstraction layer

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
