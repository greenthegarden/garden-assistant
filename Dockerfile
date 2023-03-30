FROM python:3.11

WORKDIR /code

COPY requirements/base.txt requirements/prod.txt /code/

RUN pip install --no-cache-dir --upgrade -r /code/prod.txt

COPY ./app /code/app

COPY ./templates /code/templates

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
