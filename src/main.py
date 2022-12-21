"""
Defines Rest API endpoints.

Note: order matters for overloaded paths (https://fastapi.tiangolo.com/tutorial/path-params/#order-matters).
"""
from fastapi import FastAPI, Query, Body
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from sqlalchemy import select

import argparse
import requests
import tomllib
import uvicorn

from database.setup import connect_to_database, populate_database
from database.models import Dataset, Publication
from connectors import openml

with open("config.toml", "rb") as fh:
    config = tomllib.load(fh)

username = config.get("database", {}).get("name", "root")
password = config.get("database", {}).get("password", "ok")
host = config.get("database", {}).get("host", "demodb")
port = config.get("database", {}).get("port", 3306)
database = config.get("database", {}).get("database", "aiod")

db_url = f"mysql://{username}:{password}@{host}:{port}/{database}"

parser = argparse.ArgumentParser(
    description="Please refer to the README."
)

parser.add_argument(
    "--rebuild-db",
    default="only-if-empty",
    choices=["no", "only-if-empty", "always"],
    help="Determines if the database is recreated.",
)

parser.add_argument(
    "--populate",
    default="example",
    choices=["nothing", "example", "openml"],
    help="Determines if the database gets populated with data.",
)

parser.add_argument(
    "--reload",
    action="store_true",
    help="Use `--reload` for FastAPI.",
)

args = parser.parse_args()

delete_before_create = (args.rebuild_db == "always")
engine = connect_to_database(db_url, delete_first=delete_before_create)

if args.populate in ["example", "openml"]:
    populate_database(engine, data=args.populate, only_if_empty=True)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home() -> list[str]:
    """ Homepage, provides the README. """
    with open("README.md", 'r') as fh:
        return (
            "<html></head><body>"
            + "Visit endpoint `/docs` for documentation on the REST API.</br>"
            + '</br>'.join(fh.readlines())
            + "</body></html>"
        )


@app.get("/datasets/")
def list_datasets(platforms: list[str] | None = Query(default=[])) -> list[dict]:
    """ Lists all datasets registered with AIoD.

    Query Parameter
    ------
     * platforms, list[str], optional: if provided, list only datasets from the given platform.
    """
    with Session(engine) as session:
        return [
            dataset.to_dict(depth=0)
            for dataset in session.scalars(select(Dataset)).all()
            if not platforms or dataset.platform in platforms
        ]


@app.get("/dataset/{identifier}")
def get_dataset(identifier: str) -> dict:
    """ Retrieve all meta-data for a specific dataset. """
    with Session(engine) as session:
        query = select(Dataset).where(Dataset.id == identifier)
        dataset = session.scalars(query).first()
        if not dataset:
            return {"error": f"Dataset '{identifier}' not found."}

        if dataset.platform == "openml":
            dataset_json = openml.fetch_dataset(dataset)
        else:
            raise NotImplementedError(f"No connector for platform '{dataset.platform}' available.")

        return {**dataset_json, **dataset.to_dict(depth=1)}


@app.post("/register/dataset/")
def register_dataset(
        name: str = Body(min_length=1, max_length=50),
        platform: str = Body(min_length=1, max_length=30),
        platform_identifier: str = Body(min_length=1, max_length=100)
) -> dict:
    """ Register a dataset with AIoD.

    Expects a JSON body with the following key/values:
     - name (max 50 characters): Name of the dataset.
     - platform (max 30 characters): Name of the platform on which the dataset resides.
     - platform_identifier (max 100 characters):
        Identifier which uniquely defines the dataset for the platform.
        For example, with OpenML that is the dataset id.
    """
    # Alternatively, consider defining Pydantic models instead to define the request body:
    # https://fastapi.tiangolo.com/tutorial/body/#request-body

    with Session(engine) as session:
        new_dataset = Dataset(
            name=name,
            platform=platform,
            platform_specific_identifier=platform_identifier
        )
        session.add(new_dataset)
        session.commit()
        return new_dataset.to_dict(depth=1)


@app.get("/publications")
def list_publications() -> list[dict]:
    """ Lists all publications registered with AIoD. """
    with Session(engine) as session:
        return [
            publication.to_dict(depth=0)
            for publication in session.scalars(select(Publication)).all()
        ]


@app.get("/publication/{identifier}")
def get_publication(identifier: str) -> dict:
    """ Retrieves all information for a specific publication registered with AIoD. """
    with Session(engine) as session:
        query = select(Publication).where(Publication.id == identifier)
        publication = session.scalars(query).first()
        if not publication:
            return {"error": f"Publication '{identifier}' not found."}
        return publication.to_dict(depth=1)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
