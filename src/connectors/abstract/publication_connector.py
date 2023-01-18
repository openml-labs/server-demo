import abc

from database.models import Publication


class PublicationConnector(abc.ABC):
    """Abstract class stating which methods are expected on a PublicationConnector"""

    @abc.abstractmethod
    def platform(self) -> str:
        """The platform name of this connector (e.g. 'openml' or 'huggingface')"""
        pass

    @abc.abstractmethod
    def fetch_all(self) -> list[Publication]:
        """"""
        pass
