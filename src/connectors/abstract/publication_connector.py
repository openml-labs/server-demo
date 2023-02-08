import abc
from typing import Iterator

from connectors.platforms import Platform
from database.models import Publication


class PublicationConnector(abc.ABC):
    """For every platform that offers publications, this PublicationConnector should be
    implemented."""

    @property
    def platform(self) -> Platform:
        """The platform of this connector"""
        return Platform.from_class(self.__class__)

    @abc.abstractmethod
    def fetch_all(self) -> Iterator[Publication]:
        """Retrieve all publications"""
        pass
