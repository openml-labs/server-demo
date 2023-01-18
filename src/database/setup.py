"""
Utility functions for initializing the database and tables through SQLAlchemy.
"""

from sqlalchemy import Engine, text, create_engine, select
from sqlalchemy.orm import Session

import connectors
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


def populate_database(
    engine: Engine,
    only_if_empty: bool = True,
    platform_data: str = "example",
    platform_publications="example",
):
    """Add some data to the Dataset and Publication tables.

    platform_data: str (default="example"): One of "nothing", "example" or "openml".
    platform_publications: str (default="example"): One of "nothing" or "example".
    """

    if platform_data == "nothing":
        datasets = []
    else:
        dataset_connector = connectors.dataset_connectors.get(platform_data, None)
        if dataset_connector is None:
            possibilities = ", ".join(f"`{c}`" for c in connectors.dataset_connectors.keys())
            msg = f"{platform_data=}, but must be one of {possibilities}"
            raise NotImplementedError(msg)
        datasets = dataset_connector.fetch_all()
    if platform_publications == "nothing":
        publications = []
    else:
        publication_connector = connectors.publication_connectors.get(platform_publications, None)
        if publication_connector is None:
            possibilities = ", ".join(f"`{c}`" for c in connectors.publication_connectors.keys())
            msg = f"{platform_publications=}, but must be one of {possibilities}"
            raise NotImplementedError(msg)
        publications = publication_connector.fetch_all()

    _link_datasets_with_publications(datasets, publications)
    with Session(engine) as session:
        data_exists = (
            session.scalars(select(Publication)).first() or session.scalars(select(Dataset)).first()
        )
        if only_if_empty and data_exists:
            return

        session.add_all(datasets)
        session.add_all(publications)
        session.commit()


def _link_datasets_with_publications(datasets, publications):
    """Linking some publications with some datasets. Temporary function to show the
    possibilities."""
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
    benchmark_datasets = [d for d in datasets if d.id in benchmark_dataset_ids]
    benchmark_publications = [p for p in publications if p.title == "AMLB: an AutoML Benchmark"]
    higgs_title = "Searching for exotic particles in high-energy physics with deep learning"
    higgs_publication = [p for p in publications if p.title == higgs_title]
    for publication in higgs_publication:
        publication.datasets = [d for d in datasets if d.name == "Higgs"]
    for publication in benchmark_publications:
        publication.datasets = benchmark_datasets
    return datasets, publications
