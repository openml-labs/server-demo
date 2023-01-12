import json
import tempfile
import unittest

import responses
from fastapi import FastAPI
from fastapi.testclient import TestClient

from database.models import Dataset
from main import add_routes
from tests.testutils.mocking import mocked_database_engine, add_objects_to_engine
from tests.testutils.paths import test_resources_path

OPENML_URL = "https://www.openml.org/api/v1/json"
temporary_file = tempfile.NamedTemporaryFile()


class GetOpenmlDatasetTestcase(unittest.TestCase):
    def setUp(self):
        self.engine = mocked_database_engine(temporary_file)
        app = FastAPI()
        add_routes(app, self.engine)
        self.client = TestClient(app)

    def test_happy_path(self):
        dataset_description = Dataset(name="anneal", platform="openml", platform_specific_identifier="1")

        with responses.RequestsMock() as mocked_requests:
            expected_info = GetOpenmlDatasetTestcase._mock_responses(mocked_requests, dataset_description)
            add_objects_to_engine(self.engine, dataset_description)

            response = self.client.get("/dataset/1")
        self.assertEqual(response.status_code, 200)
        response_json = response.json()

        self.assertEqual(len(response_json), 10)
        self.assertEqual(response_json['name'], expected_info['name'])
        self.assertEqual(response_json['description'], expected_info['description'])
        self.assertEqual(response_json['file_url'], expected_info['url'])
        self.assertEqual(response_json['number_of_samples'], 898)
        self.assertEqual(response_json['number_of_features'], 39)
        self.assertEqual(response_json['number_of_classes'], 5)
        self.assertEqual(response_json['platform'], "openml")
        self.assertEqual(response_json['platform_specific_identifier'], "1")
        self.assertEqual(response_json['id'], 1)
        self.assertEqual(len(response_json['publications']), 0)

    def test_dataset_not_found_in_local_db(self):
        dataset_description = Dataset(name="anneal", platform="openml", platform_specific_identifier="1")
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocked_requests:
            GetOpenmlDatasetTestcase._mock_responses(mocked_requests, dataset_description)
            add_objects_to_engine(self.engine, dataset_description)
            response = self.client.get("/dataset/2")  # Note only dataset 1 exists
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], "Dataset '2' not found in the database.")

    def test_dataset_not_found_in_openml(self):
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
            add_objects_to_engine(self.engine, dataset_description)
            response = self.client.get("/dataset/1")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], "Error while fetching data from OpenML: 'Unknown dataset'")

    @staticmethod
    def _mock_responses(mocked_requests, dataset_description: Dataset):
        """
        Mocking requests to the OpenML dependency, so that we test only our own services
        """
        with open(test_resources_path() / "connectors" / "openml" / "data_1.json", 'r') as f:
            data_response = json.load(f)
        with open(test_resources_path() / "connectors" / "openml" / "data_1_qualities.json", 'r') as f:
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


if __name__ == '__main__':
    unittest.main()
