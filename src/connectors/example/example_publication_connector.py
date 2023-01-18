from connectors.abstract.publication_connector import PublicationConnector
from database.models import Publication


class ExamplePublicationConnector(PublicationConnector):
    def platform(self) -> str:
        return "example"

    def fetch_all(self) -> list[Publication]:
        return [
            Publication(title="AMLB: an AutoML Benchmark", url="https://arxiv.org/abs/2207.12560"),
            Publication(
                title="Searching for exotic particles in high-energy physics with deep learning",
                url="https://www.nature.com/articles/ncomms5308",
            ),
        ]
