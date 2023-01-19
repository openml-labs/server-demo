from connectors.abstract.dataset_connector import DatasetConnector, DatasetMeta
from connectors.platforms import Platform
from database.models import Dataset


class ExampleDatasetConnector(DatasetConnector):
    def platform(self) -> Platform:
        return Platform.example

    def fetch(self, dataset: Dataset) -> DatasetMeta:
        return DatasetMeta(
            name=dataset.name,
            description="Example",
            file_url="test",
            number_of_classes=10,
            number_of_features=20,
            number_of_samples=30,
        )

    def fetch_all(self) -> list[Dataset]:
        return [
            Dataset(
                name="Higgs",
                platform="openml",
                platform_specific_identifier="42769",
            ),
            Dataset(
                name="porto-seguro",
                platform="openml",
                platform_specific_identifier="42742",
            ),
            Dataset(
                name="rotten_tomatoes config:default split:train",
                platform="huggingface",
                platform_specific_identifier="rotten_tomatoes|default|train",
            ),
            Dataset(
                name="rotten_tomatoes config:default split:validation",
                platform="huggingface",
                platform_specific_identifier="rotten_tomatoes|default|validation",
            ),
            Dataset(
                name="rotten_tomatoes config:default split:test",
                platform="huggingface",
                platform_specific_identifier="rotten_tomatoes|default|test",
            ),
        ]
