"""
Defines the FastAPI app
"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home() -> list[str]:
    """ Homepage, provides the README. """
    with open("README.md", 'r') as fh:
        return "<html></head><body>" + '</br>'.join(fh.readlines()) + "</body></html>"


@app.get("/datasets")
def list_datasets() -> list[dict]:
    """ Lists all datasets registered with AIoD. """
    return [{}]


@app.get("/dataset/{identifier}")
def get_dataset(identifier: str) -> dict:
    return {}


@app.get("/openml/{url:path}")
def get_openml(url: str):
    """
    Provides direct access to the OpenML JSON API.
    For more information, see `https://www.openml.org/apis`.

    Params
    ------
     * **url**, `str`: the OpenML endpoint to reach.

    Returns
    -------
    Whatever JSON the OpenML server returns for that endpoint.
    """
    openml_url = f"https://www.openml.org/api/v1/json/{url}"
    response = requests.get(openml_url)
    if response.status_code != 200:
        return f"Invalid OpenML url: {openml_url}"
    return response.json()


if __name__ == "__main__":
    uvicorn.run(app)
