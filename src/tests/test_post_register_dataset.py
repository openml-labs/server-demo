import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

import pytest
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

    response = client.post(
        "/register/dataset",
        json={"name": "dset2", "platform": "openml", "platform_identifier": "2"},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "dset2"
    assert response_json["platform"] == "openml"
    assert response_json["platform_specific_identifier"] == "2"
    assert response_json["id"] == 4
    assert response_json["publications"] == []
    assert len(response_json) == 5


@pytest.mark.parametrize(
    "name",
    ["\"'é:?", "!@#$%^&*()`~", "Ω≈ç√∫˜µ≤≥÷", "田中さんにあげて下さい", " أي بعد, ", "𝑻𝒉𝒆 𝐪𝐮𝐢𝐜𝐤", "گچپژ"],
)
def test_unicode(client: TestClient, engine: Engine, name):
    response = client.post(
        "/register/dataset", json={"name": name, "platform": "openml", "platform_identifier": "2"}
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == name


def test_duplicated_dataset(client: TestClient, engine: Engine):
    datasets = [Dataset(name="dset1", platform="openml", platform_specific_identifier="1")]
    with Session(engine) as session:
        # Populate database
        session.add_all(datasets)
        session.commit()
    response = client.post(
        "/register/dataset",
        json={"name": "dset1", "platform": "openml", "platform_identifier": "1"},
    )
    assert response.status_code == 409
    assert (
        response.json()["detail"] == "There already exists a dataset with the same platform "
        "and name, with id=1."
    )


@pytest.mark.parametrize("field", ["name", "platform", "platform_identifier"])
def test_missing_value(client: TestClient, engine: Engine, field: str):
    data = {
        "name": "Name",
        "platform": "openml",
        "platform_identifier": "1",
    }  # type: typing.Dict[str, typing.Any]
    del data[field]
    response = client.post("/register/dataset", json=data)
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"loc": ["body", field], "msg": "field required", "type": "value_error.missing"}
    ]


@pytest.mark.parametrize("field", ["name", "platform", "platform_identifier"])
def test_null_value(client: TestClient, engine: Engine, field: str):
    data = {
        "name": "Name",
        "platform": "openml",
        "platform_identifier": "1",
    }  # type: typing.Dict[str, typing.Any]
    data[field] = None
    response = client.post("/register/dataset", json=data)
    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"loc": ["body", field], "msg": "field required", "type": "value_error.missing"}
    ]
