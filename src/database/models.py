"""
Contains the definitions for the different tables in our database.
See also:
   * https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-annotated-declarative-table-type-annotated-forms-for-mapped-column
   * https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses

Note: because we use MySQL in the demo, we need to explicitly set maximum string lengths.
"""
from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, relationship


class Base(DeclarativeBase, MappedAsDataclass):
    """ Maps subclasses to Python Dataclasses, providing e.g., `__init__` automatically. """
    pass


dataset_publication_relationship = Table(
    "association_table",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id")),
    Column("publication_id", ForeignKey("publications.id")),
)


class Dataset(Base):
    """ Keeps track of which dataset is stored where. """
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(String(50))
    platform: Mapped[str] = mapped_column(String(30))
    platform_specific_identifier: Mapped[str] = mapped_column(String(100))
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    publications: Mapped[list["Publication"]] = relationship(
        default_factory=list,
        back_populates="datasets",
        secondary=dataset_publication_relationship,
    )


class Publication(Base):
    """ Any publication. """
    __tablename__ = "publications"

    title: Mapped[str] = mapped_column(String(250))
    url: Mapped[str] = mapped_column(String(250))
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    datasets: Mapped[list["Dataset"]] = relationship(
        default_factory=list,
        back_populates="publications",
        secondary=dataset_publication_relationship,
    )
