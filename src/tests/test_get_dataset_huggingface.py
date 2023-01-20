import json

import responses
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import DatasetDescription
from tests.testutils.paths import path_test_resources

HUGGINGFACE_URL = "https://datasets-server.huggingface.co"


def test_happy_path(client: TestClient, engine: Engine):
    dataset_description = DatasetDescription(
        name="rotten_tomatoes config:default split:train",
        platform="huggingface",
        platform_specific_identifier="rotten_tomatoes|default|train",
    )
    with Session(engine) as session:
        # Populate database.
        session.add(dataset_description)
        session.commit()
    with responses.RequestsMock() as mocked_requests:
        _mock_normal_responses(mocked_requests)
        response = client.get("/dataset/huggingface/rotten_tomatoes|default|train")

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["name"] == "rotten_tomatoes config:default split:train"
    assert "description" not in response_json
    expected_url = (
        "https://huggingface.co/datasets/rotten_tomatoes/resolve/"
        "refs%2Fconvert%2Fparquet/default/rotten_tomatoes-train.parquet"
    )
    assert response_json["distribution"]["contentUrl"] == expected_url
    assert response_json["distribution"]["encodingFormat"] == "parquet"
    assert response_json["size"]["value"] == 8530
    assert response_json["includedInDataCatalog"]["name"] == "HuggingFace"
    assert response_json["identifier"] == "rotten_tomatoes|default|train"


def test_dataset_not_found_in_local_db(client: TestClient, engine: Engine):
    dataset_description = DatasetDescription(
        name="rotten_tomatoes config:default split:train",
        platform="huggingface",
        platform_specific_identifier="rotten_tomatoes|default|train",
    )
    with Session(engine) as session:
        # Populate database
        session.add(dataset_description)
        session.commit()
    response = client.get("/dataset/huggingface/rotten_tomatoes|default|test")
    assert response.status_code == 404
    assert (
        response.json()["detail"] == "Dataset 'rotten_tomatoes|default|test' of 'huggingface' "
        "not found in the database."
    )


def test_dataset_not_found_in_openml(client: TestClient, engine: Engine):
    identifier = "rotten_tomatoes|default|train"
    dataset_description = DatasetDescription(
        name="name", platform="huggingface", platform_specific_identifier=identifier
    )
    with Session(engine) as session:
        # Populate database
        session.add(dataset_description)
        session.commit()
    with responses.RequestsMock() as mocked_requests:
        msg = (
            "The dataset does not exist, or is not accessible without authentication (private or "
            "gated). Please retry with authentication."
        )
        mocked_requests.add(
            responses.GET,
            "https://datasets-server.huggingface.co/splits?dataset=rotten_tomatoes",
            json={"error": msg},
            status=412,
        )
        response = client.get(f"/dataset/huggingface/{identifier}")
    assert response.status_code == 412
    assert response.json()["detail"] == f"Error while fetching splits from HuggingFace: '{msg}'"


def _mock_normal_responses(mocked_requests: responses.RequestsMock):
    """
    Mocking requests to the OpenML dependency, so that we test only our own services
    """
    huggingface_path = path_test_resources() / "connectors" / "huggingface"
    with open(huggingface_path / "splits_rotten_tomatoes.json", "r") as f:
        split_response = json.load(f)

    mocked_requests.add(
        responses.GET,
        f"{HUGGINGFACE_URL}/splits?dataset=rotten_tomatoes",
        json=split_response,
        status=200,
    )

    with open(huggingface_path / "parquet_rotten_tomatoes.json", "r") as f:
        parquet_response = json.load(f)
    mocked_requests.add(
        responses.GET,
        f"{HUGGINGFACE_URL}/parquet?dataset=rotten_tomatoes",
        json=parquet_response,
        status=200,
    )
