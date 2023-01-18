import requests
from fastapi import HTTPException

from connectors import DatasetConnector, DatasetMeta
from database.models import Dataset


class HuggingFaceDatasetConnector(DatasetConnector):
    def platform(self) -> str:
        return "huggingface"

    def fetch(self, dataset: Dataset) -> DatasetMeta:
        raise NotImplementedError("TODO(Jos)")

    def fetch_all(self) -> list[Dataset]:
        url = "https://datasets-server.huggingface.co/valid"
        response = requests.get(url)
        response_json = response.json()
        if not response.ok:
            msg = response_json["error"]["message"]
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error while fetching data from HuggingFace: '{msg}'",
            )
        return [
            Dataset(
                name=_name_from_identifier(identifier),  # e.g. tatoeba_mt
                platform=self.platform(),
                platform_specific_identifier=identifier,  # e.g. Helsinki-NLP/tatoeba_mt
            )
            for identifier in response_json["valid"]
        ]


def _name_from_identifier(identifier: str) -> str:
    """Return the part after the forward slash (if there is a forward slash)."""
    return identifier.split("/")[-1]
