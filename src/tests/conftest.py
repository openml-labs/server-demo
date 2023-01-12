import tempfile

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from starlette.testclient import TestClient

from database.models import Base
from main import add_routes


@pytest.fixture
def engine():
    temporary_file = tempfile.NamedTemporaryFile()
    engine = create_engine(f'sqlite:///{temporary_file.name}')
    Base.metadata.create_all(engine)
    yield engine


@pytest.fixture
def client(engine):
    app = FastAPI()
    add_routes(app, engine)
    yield TestClient(app)
