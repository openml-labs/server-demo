import abc

from connectors.platforms import Platform
from database.models import Publication


class PublicationConnector(abc.ABC):
    """For every platform that offers publications, this PublicationConnector should be
    implemented."""

    @abc.abstractmethod
    def platform(self) -> Platform:
        """The platform name of this connector (e.g. openml or huggingface)"""
        pass

    @abc.abstractmethod
    def fetch_all(self) -> list[Publication]:
        """Retrieve all publications"""
        pass
