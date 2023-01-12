import json

import responses
from sqlalchemy.orm import Session

from database.models import Dataset
from tests.testutils.paths import path_test_resources

OPENML_URL = "https://www.openml.org/api/v1/json"


def test_happy_path(engine, client):
    dataset_description = Dataset(name="anneal", platform="openml", platform_specific_identifier="1")

    with responses.RequestsMock() as mocked_requests:
        expected_info = _mock_responses(mocked_requests, dataset_description)
        with Session(engine) as session:
            session.add(dataset_description)
            session.commit()

        response = client.get("/dataset/1")
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json) == 10
    assert response_json['name'] == expected_info['name']
    assert response_json['description'] == expected_info['description']
    assert response_json['file_url'] == expected_info['url']
    assert response_json['number_of_samples'] == 898
    assert response_json['number_of_features'] == 39
    assert response_json['number_of_classes'] == 5
    assert response_json['platform'] == "openml"
    assert response_json['platform_specific_identifier'] == "1"
    assert response_json['id'] == 1
    assert len(response_json['publications']) == 0


def test_dataset_not_found_in_local_db(engine, client):
    dataset_description = Dataset(name="anneal", platform="openml", platform_specific_identifier="1")
    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
        _mock_responses(mocked_requests, dataset_description)
        with Session(engine) as session:
            session.add(dataset_description)
            session.commit()
        response = client.get("/dataset/2")  # Note only dataset 1 exists
    assert response.status_code == 404
    assert response.json()['detail'] == "Dataset '2' not found in the database."


def test_dataset_not_found_in_openml(engine, client):
    dataset_description = Dataset(name="anneal", platform="openml", platform_specific_identifier="1")
    with responses.RequestsMock() as mocked_requests:
        mocked_requests.add(
            responses.GET, f"{OPENML_URL}/data/{dataset_description.platform_specific_identifier}",
            json={
                "error": {
                    "code": "111",
                    "message": "Unknown dataset"
                }
            }, status=412,
        )
        with Session(engine) as session:
            session.add(dataset_description)
            session.commit()
        response = client.get("/dataset/1")
    assert response.status_code == 404
    assert response.json()['detail'] == "Error while fetching data from OpenML: 'Unknown dataset'"


def _mock_responses(mocked_requests, dataset_description: Dataset):
    """
    Mocking requests to the OpenML dependency, so that we test only our own services
    """
    with open(path_test_resources() / "connectors" / "openml" / "data_1.json", 'r') as f:
        data_response = json.load(f)
    with open(path_test_resources() / "connectors" / "openml" / "data_1_qualities.json", 'r') as f:
        data_qualities_response = json.load(f)
    mocked_requests.add(
        responses.GET, f"{OPENML_URL}/data/{dataset_description.platform_specific_identifier}",
        json=data_response, status=200,
    )
    mocked_requests.add(
        responses.GET, f"{OPENML_URL}/data/qualities/{dataset_description.platform_specific_identifier}",
        json=data_qualities_response, status=200,
    )
    return data_response['data_set_description']
