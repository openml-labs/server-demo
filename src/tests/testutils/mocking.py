from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import Base


def mocked_database_engine(temporary_file):
    """
    Mocking the sql engine, by using sqlite. All tables will be created, but not populated.
    """
    engine = create_engine(f'sqlite:///{temporary_file.name}')
    Base.metadata.create_all(engine)
    return engine


def add_object_to_engine(db_object, engine):
    """
    Add an object to the database. For testing, we use a temporary sqlite database instead of the real database.
    This mocked sqlite database starts unpopulated.
    """
    with Session(engine) as session:
        session.add(db_object)
        session.commit()
