"""
This module knows how to load an OpenML object based on its AIoD implementation,
and how to convert the OpenML response to some agreed AIoD format.
"""
import requests
from fastapi import HTTPException
from pydantic import Extra
from pydantic_schemaorg.DataCatalog import DataCatalog
from pydantic_schemaorg.DataDownload import DataDownload
from pydantic_schemaorg.Dataset import Dataset
from pydantic_schemaorg.QuantitativeValue import QuantitativeValue

from connectors.abstract.dataset_connector import DatasetConnector
from database.models import DatasetDescription

for obj in (DataCatalog, DataDownload, Dataset, QuantitativeValue):
    obj.Config.extra = Extra.forbid  # Throw exception on unrecognized fields


class OpenMlDatasetConnector(DatasetConnector):
    def fetch(self, dataset: DatasetDescription) -> Dataset:
        identifier = dataset.platform_specific_identifier
        url_data = f"https://www.openml.org/api/v1/json/data/{identifier}"
        response = requests.get(url_data)
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
        url_qualities = f"https://www.openml.org/api/v1/json/data/qualities/{identifier}"
        response = requests.get(url_qualities)
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

        # TODO: should we add those qualities as well? Schema.org does not have a place for it.
        # number_of_features=_as_int(qualities_json["NumberOfFeatures"]),
        # number_of_classes=_as_int(qualities_json["NumberOfClasses"]),

        result = Dataset(
            name=dataset_json["name"],
            url=url_data,
            description=dataset_json["description"],
            dateCreated=dataset_json["upload_date"],
            identifier=dataset.platform_specific_identifier,
            distribution=DataDownload(
                contentUrl=dataset_json["url"], encodingFormat=dataset_json["format"]
            ),
            size=QuantitativeValue(value=_as_int(qualities_json["NumberOfInstances"])),
            isAccessibleForFree=True,
            includedInDataCatalog=DataCatalog(name="OpenML"),
        )
        if "language" in dataset_json:
            setattr(result, "inLanguage", dataset_json["language"])
        return result

    def fetch_all(self) -> list[DatasetDescription]:
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
            DatasetDescription(
                name=dataset_json["name"],
                platform=self.platform,
                platform_specific_identifier=str(dataset_json["did"]),
            )
            for dataset_json in response_json["data"]["dataset"]
        ]


def _as_int(v: str) -> int:
    as_float = float(v)
    if not as_float.is_integer():
        raise ValueError(f"The input should be an integer, but was a float: {v}")
    return int(as_float)
