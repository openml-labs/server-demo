FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get -y install python3-dev default-libmysqlclient-dev build-essential default-mysql-client

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./src /app

#ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0"]
ENTRYPOINT ["python", "main.py"]
