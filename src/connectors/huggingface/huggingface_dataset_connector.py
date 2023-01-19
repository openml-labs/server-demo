import typing

import requests
from fastapi import HTTPException

from connectors import DatasetConnector, DatasetMeta
from connectors.platforms import Platform
from database.models import Dataset


class HuggingFaceDatasetConnector(DatasetConnector):
    ID_DELIMITER = "|"  # The platform_specific_identifier for HuggingFace consists of 3 or 4
    # parts: [namespace,] name_dataset, config and split. We need to concat these parts into a
    # single identifier. We cannot use "/" in requests, so "|" seems like a logical choice, that
    # does not occur in the names of current HuggingFace datasets.

    def platform(self) -> Platform:
        return Platform.huggingface

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

    def fetch(self, dataset: Dataset) -> DatasetMeta:
        id_splitted = dataset.platform_specific_identifier.split("|")
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

        url = "https://datasets-server.huggingface.co/splits"
        params = {"dataset": dataset_name}
        error_msg = "Error while fetching splits from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg, params=params)
        split_infos = [
            file
            for file in response_json["splits"]
            if file["config"] == config and file["split"] == split
        ]
        if len(split_infos) != 1:
            msg = (
                f"HuggingFace's split endpoint does not contain {config=}, {split=} for "
                f"dataset {dataset_name}."
            )
            raise HTTPException(status_code=404, detail=msg)
        split_info = split_infos[0]

        url = "https://datasets-server.huggingface.co/parquet"
        params = {"dataset": dataset_name}
        error_msg = "Error while fetching90 parquet data from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg, params=params)
        file_infos = [
            file
            for file in response_json["parquet_files"]
            if file["config"] == config and file["split"] == split
        ]
        if len(file_infos) != 1:
            msg = (
                f"HuggingFace's parquet endpoint does not contain {config=}, {split=} for "
                f"dataset {dataset_name}."
            )
            raise HTTPException(status_code=404, detail=msg)
        file_info = file_infos[0]

        url = "https://datasets-server.huggingface.co/first-rows"
        params = {"dataset": dataset_name, "config": config, "split": split}
        error_msg = "Error while fetching first-rows from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg, params=params)
        n_features = len(response_json["features"])

        return DatasetMeta(
            name=dataset.name,
            file_url=file_info["url"],
            number_of_samples=split_info["num_examples"],
            number_of_features=n_features,
        )

    def fetch_all(self) -> list[Dataset]:
        url = "https://datasets-server.huggingface.co/valid"
        error_msg = "Error while fetching all data from HuggingFace"
        response_json = HuggingFaceDatasetConnector._get(url, error_msg)
        return list(self._yield_datasets(response_json["valid"]))

    def _yield_datasets(self, dataset_names) -> typing.Iterator[Dataset]:
        """Yield a Dataset for each (name, config, split) combination."""
        for dataset_name in dataset_names:
            yield from self._yield_datasets_with_name(dataset_name)

    def _yield_datasets_with_name(self, dataset_name: str) -> typing.Iterator[Dataset]:
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
            yield Dataset(
                name=name_complete,
                platform=self.platform(),
                platform_specific_identifier=identifier_complete,
            )
