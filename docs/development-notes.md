# Garden Assistant Development Notes

## Project structure

Code structure updated to conform with <https://sqlmodel.tiangolo.com/tutorial/code-structure/>

## Creating venv

Information based on <https://docs.python.org/3/library/venv.html>

```powershell
python3 -m venv C:\Users\cutle\Development\garden-assistant --upgrade-deps
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Scripts\Activate.ps1
```

## Server

Run the server using

```sh
uvicorn app:app --reload
```
