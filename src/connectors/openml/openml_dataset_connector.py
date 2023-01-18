"""
This module knows how to load an OpenML object based on its AIoD implementation,
and how to convert the OpenML response to some agreed AIoD format.
"""
import requests
from fastapi import HTTPException

from connectors.abstract.dataset_connector import DatasetConnector, DatasetMeta
from database.models import Dataset


class OpenMlDatasetConnector(DatasetConnector):
    def platform(self) -> str:
        return "openml"

    def fetch(self, dataset: Dataset) -> DatasetMeta:
        identifier = dataset.platform_specific_identifier
        url = f"https://www.openml.org/api/v1/json/data/{identifier}"
        response = requests.get(url)
        if not response.ok:
            code = response.status_code
            if code == 412 and response.json()["error"]["message"] == "Unknown dataset":
                code = 404
            msg = response.json()["error"]["message"]
            raise HTTPException(
                status_code=code,
                detail=f"Error while fetching data from OpenML: '{msg}'",
            )
        dataset_json = response.json()["data_set_description"]

        # Here we can format the response into some standardized way, maybe this includes some
        # dataset characteristics. These need to be retrieved separately from OpenML:
        url = f"https://www.openml.org/api/v1/json/data/qualities/{identifier}"
        response = requests.get(url)
        if not response.ok:
            msg = response.json()["error"]["message"]
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error while fetching data qualities from OpenML: '{msg}'",
            )

        qualities_json = {
            quality["name"]: quality["value"]
            for quality in response.json()["data_qualities"]["quality"]
        }

        return DatasetMeta(
            name=dataset_json["name"],
            description=dataset_json["description"],
            file_url=dataset_json["url"],
            number_of_samples=_as_int(qualities_json["NumberOfInstances"]),
            number_of_features=_as_int(qualities_json["NumberOfFeatures"]),
            number_of_classes=_as_int(qualities_json["NumberOfClasses"]),
        )

    def fetch_all(self) -> list[Dataset]:
        url = "https://www.openml.org/api/v1/json/data/list"
        response = requests.get(url)
        response_json = response.json()
        if not response.ok:
            msg = response_json["error"]["message"]
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error while fetching data from OpenML: '{msg}'",
            )
        return [
            Dataset(
                name=dataset_json["name"],
                platform=self.platform(),
                platform_specific_identifier=str(dataset_json["did"]),
            )
            for dataset_json in response_json["data"]["dataset"]
        ]


def _as_int(v: str) -> int:
    as_float = float(v)
    if not as_float.is_integer():
        raise ValueError(f"The input should be an integer, but was a float: {v}")
    return int(as_float)
