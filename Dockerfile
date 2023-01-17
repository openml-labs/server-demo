FROM python:3.11-slim-bullseye

# default-mysql-client is not necessary, but can be useful when debugging connection issues.
RUN apt-get update && apt-get -y install python3-dev default-libmysqlclient-dev build-essential default-mysql-client

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml

# Create a non-root user for security
RUN groupadd -r apprunner && \
   useradd -mg apprunner apprunner \
   && chown -R apprunner:apprunner /app
USER apprunner:apprunner

# Add ~/.local/bin to the PATH. Not necessary, but can be useful for debugging and bypasses pip
# warnings.
ENV PATH="${PATH}:/home/apprunner/.local/bin"

RUN pip install .

COPY ./src /app

ENTRYPOINT ["python", "main.py"]
