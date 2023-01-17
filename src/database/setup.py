"""
Utility functions for initializing the database and tables through SQLAlchemy.
"""
from typing import Tuple

import requests
from requests import RequestException
from sqlalchemy import Engine, text, create_engine, select
from sqlalchemy.orm import Session

from .models import Base, Dataset, Publication


def connect_to_database(
    url: str = "mysql://root:ok@127.0.0.1:3307/aiod",
    create_if_not_exists: bool = True,
    delete_first: bool = False,
) -> Engine:
    """Connect to server, optionally creating the database if it does not exist.

    Params
    ------
    url: URL to the database, see https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls # noqa
    create_if_not_exists: create the database if it does not exist
    delete_first: drop the database before creating it again, to start with an empty database.
        IMPORTANT: Using `delete_first` means ALL data in that database will be lost permanently.

    Returns
    -------
    engine: Engine SQLAlchemy Engine configured with a database connection
    """
    server, database = url.rsplit("/", 1)
    engine = create_engine(server, echo=True)

    with engine.connect() as connection:
        if delete_first:
            connection.execute(text(f"DROP DATABASE IF EXISTS {database}"))
        if delete_first or create_if_not_exists:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))
        connection.execute(text(f"USE {database}"))
        if not connection.execute(text("SHOW TABLES")).all():
            Base.metadata.create_all(connection)
        connection.commit()
    return engine


def populate_database(engine: Engine, only_if_empty: bool = True, data: str = "example"):
    """Adds some data to the Dataset and Publication tables.

    data: str (default="example")
        One of "example" or "openml".
    """
    match data:
        case "example":
            datasets, publications = get_example_data()
        case "openml":
            datasets, publications = get_openml_data()
        case _:
            raise ValueError(f"`data` must be one of 'example' or 'openml': {data=}")

    with Session(engine) as session:
        data_exists = (
            session.scalars(select(Publication)).first() or session.scalars(select(Dataset)).first()
        )
        if only_if_empty and data_exists:
            return

        session.add_all(datasets)
        session.add_all(publications)
        session.commit()


def get_example_data() -> Tuple[list[Dataset], list[Publication]]:
    """Generate some toy data: 2 datasets and 2 publications."""
    datasets = [
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

    publications = [
        Publication(
            title="AMLB: an AutoML Benchmark",
            url="https://arxiv.org/abs/2207.12560",
            datasets=datasets,
        ),
        Publication(
            title="Searching for exotic particles in high-energy physics with deep learning",
            url="https://www.nature.com/articles/ncomms5308",
            datasets=[datasets[0]],
        ),
    ]
    return datasets, publications


def get_openml_data() -> Tuple[list[Dataset], list[Publication]]:
    """Generate data based on OpenML datasets and the AutoML benchmark."""
    benchmark_dataset_ids = [
        181,
        1111,
        1596,
        1457,
        40981,
        40983,
        23517,
        1489,
        31,
        40982,
        41138,
        41163,
        41164,
        41143,
        1169,
        41167,
        41147,
        41158,
        1487,
        54,
        41144,
        41145,
        41156,
        41157,
        41168,
        4541,
        1515,
        188,
        1464,
        1494,
        1468,
        1049,
        23,
        40975,
        12,
        1067,
        40984,
        40670,
        3,
        40978,
        4134,
        40701,
        1475,
        4538,
        4534,
        41146,
        41142,
        40498,
        40900,
        40996,
        40668,
        4135,
        1486,
        41027,
        1461,
        1590,
        41169,
        41166,
        41165,
        40685,
        41159,
        41161,
        41150,
        41162,
        42733,
        42734,
        42732,
        42746,
        42742,
        42769,
        43072,
    ]
    benchmark_datasets = []
    datasets = []

    for i in range(50_000):
        url = f"https://www.openml.org/api/v1/json/data/{i}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
        except RequestException:
            continue

        dataset = Dataset(
            name=response.json()["data_set_description"]["name"],
            platform="openml",
            platform_specific_identifier=str(i),
        )
        datasets.append(dataset)
        if i in benchmark_dataset_ids:
            benchmark_datasets.append(dataset)

    publications = [
        Publication(
            title="AMLB: an AutoML Benchmark",
            url="https://arxiv.org/abs/2207.12560",
            datasets=benchmark_datasets,
        ),
        Publication(
            title="Searching for exotic particles in high-energy physics with deep learning",
            url="https://www.nature.com/articles/ncomms5308",
            datasets=[dataset for dataset in datasets if dataset.name == "Higgs"],
        ),
    ]
    return datasets, publications
