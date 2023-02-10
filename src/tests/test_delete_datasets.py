import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

import pytest
from sqlalchemy import Engine, select, func
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import DatasetDescription


@pytest.mark.parametrize("identifier", ["1", "2", "3"])
def test_happy_path(client: TestClient, engine: Engine, identifier: str):
    datasets = [
        DatasetDescription(name="dset1", node="openml", node_specific_identifier="1"),
        DatasetDescription(name="dset1", node="other_node", node_specific_identifier="1"),
        DatasetDescription(name="dset2", node="other_node", node_specific_identifier="2"),
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(datasets)
        session.commit()

    assert _n_datasets(engine) == 3
    response = client.delete(f"/datasets/{identifier}")
    assert response.status_code == 200
    assert _n_datasets(engine) == 2


@pytest.mark.parametrize("identifier", ["4", "5"])
def test_nonexistent_dataset(client: TestClient, engine: Engine, identifier: str):
    datasets = [
        DatasetDescription(name="dset1", node="openml", node_specific_identifier="1"),
        DatasetDescription(name="dset1", node="other_node", node_specific_identifier="1"),
        DatasetDescription(name="dset2", node="other_node", node_specific_identifier="2"),
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(datasets)
        session.commit()

    assert _n_datasets(engine) == 3
    response = client.delete(f"/datasets/{identifier}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Dataset '{identifier}' not found in the database."
    assert _n_datasets(engine) == 3


def _n_datasets(engine: Engine) -> int:
    with Session(engine) as session:
        statement = select(func.count()).select_from(DatasetDescription)
        return session.execute(statement).scalar()
