from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import DatasetDescription


def test_unexisting_node(client: TestClient, engine: Engine):
    dataset_description = DatasetDescription(
        name="anneal", node="unexisting_node", node_specific_identifier="1"
    )
    with Session(engine) as session:
        # Populate database
        session.add(dataset_description)
        session.commit()
    response = client.get("/nodes/unexisting_node/datasets/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Node 'unexisting_node' not recognized."


def test_wrong_node(client: TestClient, engine: Engine):
    dataset_description = DatasetDescription(
        name="anneal", node="example", node_specific_identifier="1"
    )
    with Session(engine) as session:
        # Populate database
        session.add(dataset_description)
        session.commit()
    response = client.get("/nodes/openml/datasets/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset '1' of 'openml' not found in the database."
