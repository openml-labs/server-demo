import json

import responses
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from database.models import Publication, Dataset
from database.setup import populate_database
from tests.testutils.paths import path_test_resources

OPENML_URL = "https://www.openml.org/api/v1/json"
HUGGINGFACE_URL = "https://datasets-server.huggingface.co"


def test_example_happy_path(engine: Engine):
    populate_database(engine, platform_data="example", platform_publications="example")
    with Session(engine) as session:
        datasets = session.scalars(select(Dataset)).all()
        publications = session.scalars(select(Publication)).all()
        assert len(datasets) == 2
        assert len(publications) == 2
        assert {len(d.publications) for d in datasets} == {1, 2}
        assert {len(p.datasets) for p in publications} == {1, 2}


def test_openml_happy_path(engine: Engine):
    with responses.RequestsMock() as mocked_requests:
        with open(path_test_resources() / "connectors" / "openml" / "data_list.json", "r") as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, f"{OPENML_URL}/data/list", json=response, status=200)
        populate_database(engine, platform_data="openml", platform_publications="example")

    with Session(engine) as session:
        datasets = session.scalars(select(Dataset)).all()
        publications = session.scalars(select(Publication)).all()
        assert len(datasets) == 5
        assert len(publications) == 2
        assert {len(d.publications) for d in datasets} == {0, 1}
        assert {len(p.datasets) for p in publications} == {0, 1}


def test_huggingface_happy_path(engine: Engine):
    with responses.RequestsMock() as mocked_requests:
        with open(
            path_test_resources() / "connectors" / "huggingface" / "data_list.json", "r"
        ) as f:
            response = json.load(f)
        mocked_requests.add(responses.GET, f"{HUGGINGFACE_URL}/valid", json=response, status=200)
        populate_database(engine, platform_data="huggingface", platform_publications="example")

    with Session(engine) as session:
        datasets = session.scalars(select(Dataset)).all()
        publications = session.scalars(select(Publication)).all()
        assert len(datasets) == 10
        assert len(publications) == 2
        assert {len(d.publications) for d in datasets} == {0}
        assert {len(p.datasets) for p in publications} == {0}
