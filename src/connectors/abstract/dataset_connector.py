import abc

from pydantic_schemaorg.Dataset import Dataset

from connectors.platforms import Platform
from database.models import DatasetDescription


class DatasetConnector(abc.ABC):
    """For every platform that offers datasets, this DatasetConnector should be implemented."""

    @abc.abstractmethod
    def platform(self) -> Platform:
        """The platform name of this connector (e.g. openml or huggingface)"""
        pass

    @abc.abstractmethod
    def fetch(self, dataset: DatasetDescription) -> Dataset:
        """Retrieve extra metadata for this dataset"""
        pass

    @abc.abstractmethod
    def fetch_all(self) -> list[DatasetDescription]:
        """Retrieve basic information of all datasets"""
        pass
