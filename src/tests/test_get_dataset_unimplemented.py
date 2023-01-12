import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database.models import Dataset
from main import add_routes
from tests.testutils.mocking import mocked_database_engine, add_object_to_engine

OPENML_URL = "https://www.openml.org/api/v1/json"
temporary_file = tempfile.NamedTemporaryFile()


class GetDatasetTestcase(unittest.TestCase):
    def setUp(self):
        self.engine = mocked_database_engine(temporary_file)
        app = FastAPI()
        add_routes(app, self.engine)
        self.client = TestClient(app)

    def test_unexisting_platform(self):
        dataset_description = Dataset(name="anneal", platform="unexisting_platform", platform_specific_identifier="1")

        add_object_to_engine(dataset_description, self.engine)
        response = self.client.get("/dataset/1")
        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.json()['detail'], "No connector for platform 'unexisting_platform' available.")


if __name__ == '__main__':
    unittest.main()
