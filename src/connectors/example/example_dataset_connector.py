import typing

from pydantic_schemaorg.DataCatalog import DataCatalog
from pydantic_schemaorg.DataDownload import DataDownload
from pydantic_schemaorg.Dataset import Dataset
from pydantic_schemaorg.QuantitativeValue import QuantitativeValue

from connectors.abstract.dataset_connector import DatasetConnector
from database.models import DatasetDescription


class ExampleDatasetConnector(DatasetConnector):
    def fetch(self, dataset: DatasetDescription) -> Dataset:
        return Dataset(
            name=dataset.name,
            identifier=dataset.platform_specific_identifier,
            distribution=DataDownload(contentUrl="example.url", encodingFormat="application/json"),
            size=QuantitativeValue(value=1000),
            isAccessibleForFree=True,
            includedInDataCatalog=DataCatalog(name=dataset.platform),
        )

    def fetch_all(self) -> typing.Iterator[DatasetDescription]:
        yield from (
            DatasetDescription(
                name="Higgs",
                platform="openml",
                platform_specific_identifier="42769",
            ),
            DatasetDescription(
                name="porto-seguro",
                platform="openml",
                platform_specific_identifier="42742",
            ),
            DatasetDescription(
                name="rotten_tomatoes config:default split:train",
                platform="huggingface",
                platform_specific_identifier="rotten_tomatoes|default|train",
            ),
            DatasetDescription(
                name="rotten_tomatoes config:default split:validation",
                platform="huggingface",
                platform_specific_identifier="rotten_tomatoes|default|validation",
            ),
            DatasetDescription(
                name="rotten_tomatoes config:default split:test",
                platform="huggingface",
                platform_specific_identifier="rotten_tomatoes|default|test",
            ),
        )
