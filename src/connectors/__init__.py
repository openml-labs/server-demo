import typing  # noqa:F401 (flake8 raises incorrect 'Module imported but unused' error)

from .abstract.dataset_connector import DatasetConnector, DatasetMeta  # noqa:F401
from .abstract.publication_connector import PublicationConnector  # noqa:F401
from .example.example_dataset_connector import ExampleDatasetConnector
from .example.example_publication_connector import ExamplePublicationConnector
from .huggingface.huggingface_dataset_connector import HuggingFaceDatasetConnector
from .openml.openml_dataset_connector import OpenMlDatasetConnector
from .platforms import Platform  # noqa:F401

dataset_connectors = {
    c.platform(): c
    for c in (ExampleDatasetConnector(), OpenMlDatasetConnector(), HuggingFaceDatasetConnector())
}  # type: typing.Dict[Platform, DatasetConnector]

publication_connectors = {
    p.platform(): p for p in (ExamplePublicationConnector(),)
}  # type: typing.Dict[Platform, PublicationConnector]
