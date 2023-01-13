from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import Dataset


def test_unexisting_platform(client: TestClient, engine: Engine):
    dataset_description = Dataset(name="anneal", platform="unexisting_platform", platform_specific_identifier="1")
    with Session(engine) as session:
        # Populate database
        session.add(dataset_description)
        session.commit()
    response = client.get("/dataset/1")
    assert response.status_code == 501
    assert response.json()['detail'] == "No connector for platform 'unexisting_platform' available."
