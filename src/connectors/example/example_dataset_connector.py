from connectors.abstract.dataset_connector import DatasetConnector, DatasetMeta
from database.models import Dataset


class ExampleDatasetConnector(DatasetConnector):
    def platform(self) -> str:
        return "example"

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
        ]
