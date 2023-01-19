import abc
from dataclasses import dataclass

from connectors.platforms import Platform
from database.models import Dataset


@dataclass
class DatasetMeta:
    name: str
    file_url: str
    number_of_samples: int
    number_of_features: int
    description: str | None = None
    number_of_classes: int | None = None


class DatasetConnector(abc.ABC):
    """For every platform that offers datasets, this DatasetConnector should be implemented."""

    @abc.abstractmethod
    def platform(self) -> Platform:
        """The platform name of this connector (e.g. openml or huggingface)"""
        pass

    @abc.abstractmethod
    def fetch(self, dataset: Dataset) -> DatasetMeta:
        """Retrieve extra metadata for this dataset"""
        pass

    @abc.abstractmethod
    def fetch_all(self) -> list[Dataset]:
        """Retrieve basic information of all datasets"""
        pass
