from sqlalchemy import Engine
from starlette.testclient import TestClient

from connectors import ExampleDatasetConnector, ExamplePublicationConnector
from database.setup import populate_database


def test_get_happy_path(client: TestClient, engine: Engine):
    populate_database(
        engine,
        dataset_connectors=[ExampleDatasetConnector()],
        publications_connectors=[ExamplePublicationConnector()],
    )

    publications = _get_publications(client, "1")
    assert {pub["title"] for pub in publications} == {
        "AMLB: an AutoML Benchmark",
        "Searching for exotic particles in high-energy physics with deep learning",
    }
    assert {pub["url"] for pub in publications} == {
        "https://arxiv.org/abs/2207.12560",
        "https://www.nature.com/articles/ncomms5308",
    }
    assert {pub["id"] for pub in publications} == {1, 2}
    for pub in publications:
        assert len(pub) == 3


def test_post_happy_path(client: TestClient, engine: Engine):
    populate_database(
        engine,
        dataset_connectors=[ExampleDatasetConnector()],
        publications_connectors=[ExamplePublicationConnector()],
    )
    assert len(_get_publications(client, "3")) == 0
    response = client.post("/datasets/3/publications/1")
    assert response.status_code == 200
    assert len(_get_publications(client, "3")) == 1
    response = client.post("/datasets/3/publications/2")
    assert response.status_code == 200
    publications = _get_publications(client, "3")
    assert len(publications) == 2
    assert {pub["id"] for pub in publications} == {1, 2}


def test_post_duplicate(client: TestClient, engine: Engine):
    populate_database(
        engine,
        dataset_connectors=[ExampleDatasetConnector()],
        publications_connectors=[ExamplePublicationConnector()],
    )
    client.post("/datasets/3/publications/1")
    response = client.post("/datasets/3/publications/1")
    assert response.status_code == 409
    assert response.json()["detail"] == "Dataset 3 is already linked to publication 1."


def test_delete(client: TestClient, engine: Engine):
    populate_database(
        engine,
        dataset_connectors=[ExampleDatasetConnector()],
        publications_connectors=[ExamplePublicationConnector()],
    )
    assert len(_get_publications(client, "1")) == 2
    response = client.delete("/datasets/1/publications/1")
    assert response.status_code == 200
    assert len(_get_publications(client, "1")) == 1


def test_delete_nonexistent(client: TestClient, engine: Engine):
    populate_database(
        engine,
        dataset_connectors=[ExampleDatasetConnector()],
        publications_connectors=[ExamplePublicationConnector()],
    )
    response = client.delete("/datasets/1/publications/3")
    assert response.status_code == 404
    assert response.json()["detail"] == "Publication '3' not found in the database."


def _get_publications(client: TestClient, identifier: str):
    response = client.get(f"/datasets/{identifier}/publications")
    assert response.status_code == 200
    return response.json()
