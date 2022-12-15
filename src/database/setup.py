"""
Utility functions for initializing the database and tables through SQLAlchemy.
"""
from sqlalchemy import Engine, text, create_engine
from sqlalchemy.orm import Session

from models import Base, Dataset, Publication


def connect_to_database(
        url: str = "mysql://root:ok@127.0.0.1:3307/aiod",
        create_if_not_exists: bool = True,
        delete_first: bool = False,
) -> Engine:
    """Connect to server, optionally creating the database if it does not exist.

    url: URL to the database, see https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls
    create_if_not_exists: create the database if it does not exist
    delete_first: drop the database before creating it again, to start with an empty database.
        IMPORTANT: Using `delete_first` means ALL data in that database will be lost permanently.
    """
    server, database = url.rsplit("/", 1)
    engine = create_engine(server, echo=True)

    with engine.connect() as connection:
        if delete_first:
            connection.execute(text(f"DROP DATABASE IF EXISTS {database}"))
        if delete_first or create_if_not_exists:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))
        connection.execute(text(f"USE {database}"))
        connection.commit()

    return engine


def populate_database(engine: Engine):
    """ Adds some toy data to the dataset. """
    Base.metadata.create_all(engine)
    datasets = [
        Dataset(
            name="Higgs",
            platform="OpenML",
            platform_specific_identifier="42769",
        ),
        Dataset(
            name="porto-seguro",
            platform="OpenML",
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
        ),
    ]

    with Session(engine) as session:
        session.add_all(datasets)
        session.add_all(publications)

        session.commit()
