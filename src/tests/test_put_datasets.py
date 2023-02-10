import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import DatasetDescription


@pytest.mark.parametrize(
    "identifier,name,node,node_specific_identifier",
    [
        (1, "NEW NAME", "openml", "1"),
        (1, "dset1", "openml", "new-id"),
        (1, "dset1", "other_node", "3"),
        (3, "DSET2", "other_node", "3"),
    ],
)
def test_happy_path(
    client: TestClient,
    engine: Engine,
    identifier: int,
    name: str,
    node: str,
    node_specific_identifier: str,
):
    _setup(engine)
    response = client.put(
        f"/datasets/{identifier}",
        json={"name": name, "node": node, "node_specific_identifier": node_specific_identifier},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == name
    assert response_json["node"] == node
    assert response_json["node_specific_identifier"] == node_specific_identifier
    assert response_json["id"] == identifier
    assert len(response_json) == 5


def test_non_existent(client: TestClient, engine: Engine):
    _setup(engine)

    response = client.put(
        "/datasets/4",
        json={"name": "name", "node": "node", "node_specific_identifier": "id"},
    )
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Dataset '4' not found in the database."


def test_partial_update(client: TestClient, engine: Engine):
    _setup(engine)

    response = client.put("/datasets/4", json={"name": "name"})
    # Partial update: node and node_specific_identifier omitted. This is not supported,
    # and should be a PATCH request if we supported it.

    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"] == [
        {"loc": ["body", "node"], "msg": "field required", "type": "value_error.missing"},
        {
            "loc": ["body", "node_specific_identifier"],
            "msg": "field required",
            "type": "value_error.missing",
        },
    ]


def test_too_long_name(client: TestClient, engine: Engine):
    _setup(engine)

    name = "a" * 200
    response = client.put(
        "/datasets/4",
        json={"name": name, "node": "node", "node_specific_identifier": "id"},
    )
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"] == [
        {
            "ctx": {"limit_value": 150},
            "loc": ["body", "name"],
            "msg": "ensure this value has at most 150 characters",
            "type": "value_error.any_str.max_length",
        }
    ]


def _setup(engine):
    datasets = [
        DatasetDescription(name="dset1", node="openml", node_specific_identifier="1"),
        DatasetDescription(name="dset1", node="other_node", node_specific_identifier="1"),
        DatasetDescription(name="dset2", node="other_node", node_specific_identifier="2"),
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(datasets)
        session.commit()
