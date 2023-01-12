import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database.models import Dataset
from main import add_routes
from tests.testutils.mocking import mocked_database_engine, add_objects_to_engine

temporary_file = tempfile.NamedTemporaryFile()


class GetDatasetsTestcase(unittest.TestCase):
    def setUp(self):
        self.engine = mocked_database_engine(temporary_file)
        app = FastAPI()
        add_routes(app, self.engine)
        self.client = TestClient(app)

    def test_happy_path(self):
        datasets = [Dataset(name="dset1", platform="openml", platform_specific_identifier="1"),
                    Dataset(name="dset1", platform="other_platform", platform_specific_identifier="1"),
                    Dataset(name="dset2", platform="other_platform", platform_specific_identifier="2"),
                    ]
        add_objects_to_engine(self.engine, *datasets)

        response = self.client.get("/datasets")
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(len(response_json), 3)
        self.assertEqual({ds['name'] for ds in response_json}, {"dset1", "dset2"})
        self.assertEqual({ds['platform'] for ds in response_json}, {"openml", "other_platform"})
        self.assertEqual({ds['platform_specific_identifier'] for ds in response_json}, {"1", "2"})
        self.assertEqual({ds['id'] for ds in response_json}, {1, 2, 3})
        for ds in response_json:
            self.assertEqual(len(ds), 4)


if __name__ == '__main__':
    unittest.main()
