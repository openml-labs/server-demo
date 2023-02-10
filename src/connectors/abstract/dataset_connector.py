import abc
from typing import Iterator

from pydantic_schemaorg.Dataset import Dataset

from connectors.node_names import NodeName
from database.models import DatasetDescription


class DatasetConnector(abc.ABC):
    """For every node that offers datasets, this DatasetConnector should be implemented."""

    @property
    def node_name(self) -> NodeName:
        """The node of this connector"""
        return NodeName.from_class(self.__class__)

    @abc.abstractmethod
    def fetch(self, dataset: DatasetDescription) -> Dataset:
        """Retrieve extra metadata for this dataset"""
        pass

    @abc.abstractmethod
    def fetch_all(self, limit: int | None) -> Iterator[DatasetDescription]:
        """Retrieve basic information of all datasets"""
        pass
