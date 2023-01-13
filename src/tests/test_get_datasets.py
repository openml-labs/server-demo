from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import Dataset


def test_happy_path(client: TestClient, engine: Engine):
    datasets = [
        Dataset(name="dset1", platform="openml", platform_specific_identifier="1"),
        Dataset(name="dset1", platform="other_platform", platform_specific_identifier="1"),
        Dataset(name="dset2", platform="other_platform", platform_specific_identifier="2"),
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(datasets)
        session.commit()

    response = client.get("/datasets")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 3
    assert {ds["name"] for ds in response_json} == {"dset1", "dset2"}
    assert {ds["platform"] for ds in response_json} == {"openml", "other_platform"}
    assert {ds["platform_specific_identifier"] for ds in response_json} == {"1", "2"}
    assert {ds["id"] for ds in response_json} == {1, 2, 3}
    for ds in response_json:
        assert len(ds) == 4
