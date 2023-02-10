from sqlalchemy import Engine
from starlette.testclient import TestClient

from connectors import ExampleDatasetConnector, ExamplePublicationConnector
from database.setup import populate_database


def test_happy_path(client: TestClient, engine: Engine):
    populate_database(
        engine,
        dataset_connector=ExampleDatasetConnector(),
        publications_connector=ExamplePublicationConnector(),
    )

    response = client.get("/datasets/1/publications")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert {pub["title"] for pub in response_json} == {
        "AMLB: an AutoML Benchmark",
        "Searching for exotic particles in high-energy physics with deep learning",
    }
    assert {pub["url"] for pub in response_json} == {
        "https://arxiv.org/abs/2207.12560",
        "https://www.nature.com/articles/ncomms5308",
    }
    assert {pub["id"] for pub in response_json} == {1, 2}
    for pub in response_json:
        assert len(pub) == 3
