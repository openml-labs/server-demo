import abc
from dataclasses import dataclass

from database.models import Dataset


@dataclass
class DatasetMeta:
    name: str
    description: str
    file_url: str
    number_of_samples: int
    number_of_features: int
    number_of_classes: int


class DatasetConnector(abc.ABC):
    """Abstract class stating which methods are expected on a DatasetConnector"""

    @abc.abstractmethod
    def platform(self) -> str:
        """The platform name of this connector (e.g. 'openml' or 'huggingface')"""
        pass

    @abc.abstractmethod
    def fetch(self, dataset: Dataset) -> DatasetMeta:
        """Retrieve extra metadata for this dataset"""
        pass

    @abc.abstractmethod
    def fetch_all(self) -> list[Dataset]:
        """Retrieve all dataset descriptions"""
        pass
