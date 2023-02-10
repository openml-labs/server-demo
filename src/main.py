"""
Defines Rest API endpoints.

Note: order matters for overloaded paths
(https://fastapi.tiangolo.com/tutorial/path-params/#order-matters).
"""
import argparse
import tomllib
import traceback
from typing import Dict

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select, Engine, and_, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import connectors
import schemas
from connectors import NodeName
from database.models import DatasetDescription, Publication
from database.setup import connect_to_database, populate_database


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Please refer to the README.")
    parser.add_argument(
        "--rebuild-db",
        default="only-if-empty",
        choices=["no", "only-if-empty", "always"],
        help="Determines if the database is recreated.",
    )
    parser.add_argument(
        "--populate-datasets",
        default="example",
        choices=["nothing"] + [p.name for p in NodeName],
        help="Determines if the database gets populated with datasets.",
    )
    parser.add_argument(
        "--populate-publications",
        default="example",
        choices=["nothing"] + [p.name for p in NodeName],
        help="Determines if the database gets populated with publications.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Use `--reload` for FastAPI.",
    )
    return parser.parse_args()


def _engine(rebuild_db: str) -> Engine:
    """
    Return a SqlAlchemy engine, backed by the MySql connection as configured in the configuration
    file.
    """
    with open("config.toml", "rb") as fh:
        config = tomllib.load(fh)
    db_config = config.get("database", {})
    username = db_config.get("name", "root")
    password = db_config.get("password", "ok")
    host = db_config.get("host", "demodb")
    port = db_config.get("port", 3306)
    database = db_config.get("database", "aiod")

    db_url = f"mysql://{username}:{password}@{host}:{port}/{database}"

    delete_before_create = rebuild_db == "always"
    return connect_to_database(db_url, delete_first=delete_before_create)


def _connector_from_node_name(connector_type: str, connector_dict: Dict, node_name: str):
    """Get the connector from the connector_dict, identified by its node name."""
    if node_name == "nothing":
        return None
    try:
        node = NodeName(node_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Node '{node_name}' not recognized.")
    connector = connector_dict.get(node, None)
    if connector is None:
        possibilities = ", ".join(f"`{c}`" for c in connectors.dataset_connectors.keys())
        msg = (
            f"No {connector_type} connector for node '{node_name}' available. Possible values:"
            f" {possibilities}"
        )
        raise HTTPException(status_code=501, detail=msg)
    return connector


def _retrieve_dataset(session, identifier, node=None) -> DatasetDescription:
    if node is None:
        query = select(DatasetDescription).where(DatasetDescription.id == identifier)
    else:
        query = select(DatasetDescription).where(
            and_(
                DatasetDescription.node_specific_identifier == identifier,
                DatasetDescription.node == node,
            )
        )
    dataset = session.scalars(query).first()
    if not dataset:
        if node is None:
            msg = f"Dataset '{identifier}' not found in the database."
        else:
            msg = f"Dataset '{identifier}' of '{node}' not found in the database."
        raise HTTPException(status_code=404, detail=msg)
    return dataset


def _retrieve_publication(session, identifier) -> Publication:
    query = select(Publication).where(Publication.id == identifier)
    publication = session.scalars(query).first()
    if not publication:
        raise HTTPException(
            status_code=404,
            detail=f"Publication '{identifier}' not found in the database.",
        )
    return publication


def _wrap_as_http_exception(exception: Exception) -> HTTPException:
    if isinstance(exception, HTTPException):
        return exception

    # This is an unexpected error. A mistake on our part. End users should not be informed about
    # details of problems they are not expected to fix, so we give a generic response and log the
    # error.
    traceback.print_exc()
    return HTTPException(
        status_code=500,
        detail=(
            "Unexpected exception while processing your request. Please contact the maintainers."
        ),
    )


def add_routes(app: FastAPI, engine: Engine):
    """Add routes to the FastAPI application"""

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        """Provides a redirect page to the docs."""
        return """
        <!DOCTYPE html>
        <html>
          <head>
            <meta http-equiv="refresh" content="0; url='docs'" />
          </head>
          <body>
            <p>The REST API documentation is <a href="docs">here</a>.</p>
          </body>
        </html>
        """

    # Multiple endpoints share the same set of parameters, we define a class for easy re-use of
    # dependencies:
    # https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/?h=depends#classes-as-dependencies # noqa
    class Pagination(BaseModel):
        offset: int = 0
        limit: int = 100

    @app.get("/datasets/")
    def list_datasets(
        pagination: Pagination = Depends(Pagination),
    ) -> list[dict]:
        """Lists all datasets registered with AIoD.

        Query Parameter
        ------
         * nodes, list[str], optional: if provided, list only datasets from the given node.
        """
        # For additional information on querying through SQLAlchemy's ORM:
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
        try:
            with Session(engine) as session:
                query = select(DatasetDescription).offset(pagination.offset).limit(pagination.limit)
                return [dataset.to_dict(depth=0) for dataset in session.scalars(query).all()]
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/datasets/{identifier}")
    def get_dataset(identifier: str) -> dict:
        """Retrieve all meta-data for a specific dataset."""
        try:
            with Session(engine) as session:
                dataset = _retrieve_dataset(session, identifier)
            node = dataset.node
            connector = connectors.dataset_connectors.get(node, None)
            if connector is None:
                raise HTTPException(
                    status_code=501,
                    detail=f"No connector for node '{node}' available.",
                )
            dataset_meta = connector.fetch(dataset)
            return dataset_meta.dict()
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/nodes")
    def get_nodes() -> list:
        """Retrieve information about all known nodes"""
        return list(NodeName)

    @app.get("/nodes/{node}/datasets")
    def get_node_datasets(node: str, pagination: Pagination = Depends(Pagination)) -> list[dict]:
        """Retrieve all meta-data of the datasets of a single node."""
        try:
            with Session(engine) as session:
                query = (
                    select(DatasetDescription)
                    .where(DatasetDescription.node == node)
                    .offset(pagination.offset)
                    .limit(pagination.limit)
                )
                return [dataset.to_dict(depth=0) for dataset in session.scalars(query).all()]
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/nodes/{node}/datasets/{identifier}")
    def get_node_dataset(node: str, identifier: str) -> dict:
        """Retrieve all meta-data for a specific dataset identified by the
        node-specific-identifier."""
        try:
            connector = _connector_from_node_name("dataset", connectors.dataset_connectors, node)
            with Session(engine) as session:
                dataset = _retrieve_dataset(session, identifier, node)
            dataset_meta = connector.fetch(dataset)
            return dataset_meta.dict()
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.post("/datasets/")
    def register_dataset(dataset: schemas.Dataset) -> dict:
        """Register a dataset with AIoD."""
        try:
            with Session(engine) as session:
                new_dataset = DatasetDescription(
                    name=dataset.name,
                    node=dataset.node,
                    node_specific_identifier=dataset.node_specific_identifier,
                )
                session.add(new_dataset)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    query = select(DatasetDescription).where(
                        and_(
                            DatasetDescription.node == dataset.node,
                            DatasetDescription.name == dataset.name,
                        )
                    )
                    existing_dataset = session.scalars(query).first()
                    raise HTTPException(
                        status_code=409,
                        detail="There already exists a dataset with the same "
                        f"node and name, with id={existing_dataset.id}.",
                    )
                return new_dataset.to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.put("/datasets/{identifier}")
    def put_dataset(identifier: str, dataset: schemas.Dataset) -> dict:
        """Update an existing dataset."""
        try:
            with Session(engine) as session:
                _retrieve_dataset(session, identifier)  # Raise error if dataset does not exist
                statement = (
                    update(DatasetDescription)
                    .values(
                        node=dataset.node,
                        name=dataset.name,
                        node_specific_identifier=dataset.node_specific_identifier,
                    )
                    .where(DatasetDescription.id == identifier)
                )
                session.execute(statement)
                session.commit()
                return _retrieve_dataset(session, identifier).to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.delete("/datasets/{identifier}")
    def delete_dataset(identifier: str):
        try:
            with Session(engine) as session:
                _retrieve_dataset(session, identifier)  # Raise error if it does not exist

                statement = delete(DatasetDescription).where(DatasetDescription.id == identifier)
                session.execute(statement)
                session.commit()
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/publications")
    def list_publications(pagination: Pagination = Depends(Pagination)) -> list[dict]:
        """Lists all publications registered with AIoD."""
        try:
            with Session(engine) as session:
                return [
                    publication.to_dict(depth=0)
                    for publication in session.scalars(
                        select(Publication).offset(pagination.offset).limit(pagination.limit)
                    ).all()
                ]
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.post("/publications")
    def register_publication(publication: schemas.Publication) -> dict:
        """Add a publication."""
        try:
            with Session(engine) as session:
                new_publication = Publication(title=publication.title, url=publication.url)
                session.add(new_publication)
                session.commit()
                return new_publication.to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/publications/{identifier}")
    def get_publication(identifier: str) -> dict:
        """Retrieves all information for a specific publication registered with AIoD."""
        try:
            with Session(engine) as session:
                publication = _retrieve_publication(session, identifier)
                return publication.to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.put("/publications/{identifier}")
    def update_publication(identifier: str, publication: schemas.Publication) -> dict:
        """Update this publication"""
        try:
            with Session(engine) as session:
                _retrieve_publication(session, identifier)  # Raise error if dataset does not exist
                statement = (
                    update(Publication)
                    .values(
                        title=publication.title,
                        url=publication.url,
                    )
                    .where(Publication.id == identifier)
                )
                session.execute(statement)
                session.commit()
                return _retrieve_publication(session, identifier).to_dict(depth=1)
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.delete("/publications/{identifier}")
    def delete_publication(identifier: str):
        """Delete this publication from AIoD."""
        try:
            with Session(engine) as session:
                _retrieve_publication(session, identifier)  # Raise error if it does not exist

                statement = delete(Publication).where(Publication.id == identifier)
                session.execute(statement)
                session.commit()
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.get("/datasets/{identifier}/publications")
    def list_publications_related_to_dataset(identifier: str) -> list[dict]:
        """Lists all publications registered with AIoD that use this dataset."""
        try:
            with Session(engine) as session:
                dataset = _retrieve_dataset(session, identifier)
                return [publication.to_dict(depth=0) for publication in dataset.publications]
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.post("/datasets/{dataset_id}/publications/{publication_id}")
    def relate_publication_to_dataset(dataset_id: str, publication_id: str):
        try:
            with Session(engine) as session:
                dataset = _retrieve_dataset(session, dataset_id)
                publication = _retrieve_publication(session, publication_id)
                if publication in dataset.publications:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Dataset {dataset_id} is already linked to publication "
                        f"{publication_id}.",
                    )
                dataset.publications.append(publication)
                session.commit()
        except Exception as e:
            raise _wrap_as_http_exception(e)

    @app.delete("/datasets/{dataset_id}/publications/{publication_id}")
    def delete_relation_publication_to_dataset(dataset_id: str, publication_id: str):
        try:
            with Session(engine) as session:
                dataset = _retrieve_dataset(session, dataset_id)
                publication = _retrieve_publication(session, publication_id)
                if publication not in dataset.publications:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Dataset {dataset_id} is not linked to publication "
                        f"{publication_id}.",
                    )
                dataset.publications = [p for p in dataset.publications if p != publication]
                session.commit()
        except Exception as e:
            raise _wrap_as_http_exception(e)


def create_app() -> FastAPI:
    """Create the FastAPI application, complete with routes."""
    app = FastAPI()
    args = _parse_args()

    dataset_connector = _connector_from_node_name(
        "dataset", connectors.dataset_connectors, args.populate_datasets
    )
    publication_connector = _connector_from_node_name(
        "publication", connectors.publication_connectors, args.populate_publications
    )
    engine = _engine(args.rebuild_db)
    if not all(c is None for c in (dataset_connector, publication_connector)):
        populate_database(
            engine,
            dataset_connector=dataset_connector,
            publications_connector=publication_connector,
            only_if_empty=True,
        )
    add_routes(app, engine)
    return app


def main():
    """Run the application. Placed in a separate function, to avoid having global variables"""
    args = _parse_args()
    uvicorn.run("main:create_app", host="0.0.0.0", reload=args.reload, factory=True)


if __name__ == "__main__":
    main()
