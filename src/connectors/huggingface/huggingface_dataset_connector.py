import typing

import requests
from fastapi import HTTPException
from pydantic import Extra
from pydantic_schemaorg.DataCatalog import DataCatalog
from pydantic_schemaorg.DataDownload import DataDownload
from pydantic_schemaorg.Dataset import Dataset
from pydantic_schemaorg.QuantitativeValue import QuantitativeValue

from connectors import DatasetConnector
from database.models import DatasetDescription

for obj in (DataCatalog, DataDownload, Dataset, QuantitativeValue):
    obj.Config.extra = Extra.forbid  # Throw exception on unrecognized fields


class HuggingFaceDatasetConnector(DatasetConnector):
    ID_DELIMITER = "|"  # The node_specific_identifier for HuggingFace consists of 3 or 4
    # parts: [namespace,] name_dataset, config and split. We need to concat these parts into a
    # single identifier. We cannot use "/" in requests, so "|" seems like a logical choice, that
    # does not occur in the names of current HuggingFace datasets.

    @staticmethod
    def _get(
        url: str, error_msg: str, params: typing.Dict[str, typing.Any] | None = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Perform a GET request and raise an exception if the response code is not OK.
        """
        response = requests.get(url, params=params)
        response_json = response.json()
        if not response.ok:
            msg = response_json["error"]
            raise HTTPException(
                status_code=response.status_code,
                detail=f"{error_msg}: '{msg}'",
            )
        return response_json

    def fetch(self, dataset: DatasetDescription) -> Dataset:
        id_splitted = dataset.node_specific_identifier.split("|")
        if len(id_splitted) not in (3, 4):
            msg = (
                "The identifier for huggingface data should be formatted as "
                "'namespace|name_dataset|config|split', or "
                "'name_dataset|config|split' if the dataset does not have a namespace. "
                "Examples: 'Helsinki-NLP|tatoeba_mt|eng-fra|train' or "
                "'rotten_tomatoes|default|validation'"
            )
            raise HTTPException(status_code=400, detail=msg)
        dataset_name = "/".join(id_splitted[:-2])
        config = id_splitted[-2]
        split = id_splitted[-1]

        split_info = HuggingFaceDatasetConnector._fetch_item(
            url="https://datasets-server.huggingface.co/splits",
            items_name="splits",
            dataset_name=dataset_name,
            config=config,
            split=split,
        )
        file_info = HuggingFaceDatasetConnector._fetch_item(
            url="https://datasets-server.huggingface.co/parquet",
            items_name="parquet_files",
            dataset_name=dataset_name,
            config=config,
            split=split,
        )

        # TODO: decide our output format for datasets.
        #  If we want extra information, e.g. the number of features, this works:
        # url = "https://datasets-server.huggingface.co/first-rows"
        # params = {"dataset": dataset_name, "config": config, "split": split}
        # error_msg = "Error while fetching first-rows from HuggingFace"
        # response_json = HuggingFaceDatasetConnector._get(url, error_msg, params=params)
        # n_features = len(response_json["features"])

        return Dataset(
            name=dataset.name,
            identifier=dataset.node_specific_identifier,
            distribution=DataDownload(contentUrl=file_info["url"], encodingFormat="parquet"),
            size=QuantitativeValue(value=split_info["num_examples"]),
            isAccessibleForFree=True,
            includedInDataCatalog=DataCatalog(name="HuggingFace"),
        )

    @staticmethod
    def _fetch_item(url: str, items_name: str, dataset_name: str, config: str, split: str):
        """Fetching a single item (split information, or parquet file information)"""
        params = {"dataset": dataset_name}
        error_msg = f"Error while fetching {items_name} from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg, params=params)
        items = [
            file
            for file in response_json[items_name]
            if file["config"] == config and file["split"] == split
        ]
        if len(items) != 1:
            msg = (
                f"HuggingFace's {items_name} endpoint does not contain {config=}, {split=} for "
                f"dataset {dataset_name} (or returns multiple)."
            )
            raise HTTPException(status_code=404, detail=msg)
        return items[0]

    def fetch_all(self) -> typing.Iterator[DatasetDescription]:
        url = "https://datasets-server.huggingface.co/valid"
        error_msg = "Error while fetching all data from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg)
        for dataset_name in response_json["valid"]:
            yield from self._yield_datasets_with_name(dataset_name)

    def _yield_datasets_with_name(self, dataset_name: str) -> typing.Iterator[DatasetDescription]:
        """Yield a DataSet for each (config, split) combination with this name."""
        if self.ID_DELIMITER in dataset_name:
            raise ValueError(
                f"The huggingface name '{dataset_name}' contains a '{self.ID_DELIMITER}', which we "
                f"use as delimiter."
            )
        url = "https://datasets-server.huggingface.co/splits"
        params = {"dataset": dataset_name}
        error_msg = "Error while fetching splits from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg, params=params)

        for split_json in response_json["splits"]:
            config = split_json["config"]
            split = split_json["split"]
            identifier_complete = f"{dataset_name.replace('/', '|')}|{config}|{split}"
            name_complete = f"{dataset_name.split('/')[-1]} config:{config} split:{split}"
            yield DatasetDescription(
                name=name_complete,
                node=self.node_name,
                node_specific_identifier=identifier_complete,
            )
