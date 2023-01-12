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


def add_objects_to_engine(engine, *objects):
    """
    Add one or more objects to the database. For testing, we use a temporary sqlite database instead of the real
    database. This mocked sqlite database starts unpopulated.
    """
    with Session(engine) as session:
        session.add_all(objects)
        session.commit()
