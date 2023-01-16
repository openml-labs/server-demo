FROM python:3.11-slim-bullseye

# default-mysql-client is not necessary, but can be useful when debugging connection issues.
RUN apt-get update && apt-get -y install python3-dev default-libmysqlclient-dev build-essential default-mysql-client

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml

RUN pip install .

COPY ./src /app

ENTRYPOINT ["python", "main.py"]
