import tempfile
from typing import Iterator

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine, Engine
from starlette.testclient import TestClient

from database.models import Base
from main import add_routes


@pytest.fixture
def engine() -> Iterator[Engine]:
    """
    Create a SqlAlchemy engine for tests, backed by a temporary sqlite file.
    """
    temporary_file = tempfile.NamedTemporaryFile()
    engine = create_engine(f'sqlite:///{temporary_file.name}')
    Base.metadata.create_all(engine)
    yield engine  # Yielding is essential, the temporary file will be closed after the engine is used


@pytest.fixture
def client(engine: Engine) -> TestClient:
    """
    Create a TestClient that can be used to mock sending requests to our application
    """
    app = FastAPI()
    add_routes(app, engine)
    return TestClient(app)
