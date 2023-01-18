import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

from .abstract.dataset_connector import DatasetConnector, DatasetMeta  # noqa:F401
from .abstract.publication_connector import PublicationConnector  # noqa:F401
from .example.example_dataset_connector import ExampleDatasetConnector
from .example.example_publication_connector import ExamplePublicationConnector
from .openml.openml_dataset_connector import OpenMlDatasetConnector

dataset_connectors = {
    c.platform(): c for c in (ExampleDatasetConnector(), OpenMlDatasetConnector())
}  # type: typing.Dict[str, DatasetConnector]

publication_connectors = {
    p.platform(): p for p in (ExamplePublicationConnector(),)
}  # type: typing.Dict[str, PublicationConnector]
