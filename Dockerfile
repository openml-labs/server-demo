FROM python:3.11-slim-bullseye

# default-mysql-client is not necessary, but can be useful when debugging connection issues.
RUN apt-get update && apt-get -y install python3-dev default-libmysqlclient-dev build-essential default-mysql-client

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./src /app

#ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0"]
ENTRYPOINT ["python", "main.py"]
