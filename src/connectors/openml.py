"""
This module knows how to load an OpenML object based on its AIoD implementation,
and how to convert the OpenML response to some agreed AIoD format.
"""
import requests

from database.models import Dataset


def fetch_dataset(dataset: Dataset) -> dict:
    """ Retrieve dataset meta-data and dataset characteristics from OpenML. """
    url = f"https://www.openml.org/api/v1/json/data/{dataset.platform_specific_identifier}"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Unexpected response fetching dataset meta-data: {response!r}")

    dataset_json = response.json()["data_set_description"]

    # Here we can format the response into some standardized way, maybe this includes some
    # dataset characteristics. These need to be retrieved separately from OpenML:
    url = f"https://www.openml.org/api/v1/json/data/qualities/{dataset.platform_specific_identifier}"
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Unexpected response fetching dataset qualities: {response!r}")

    qualities_json = {
        quality["name"]: quality["value"]
        for quality in response.json()["data_qualities"]["quality"]
    }

    return {
        "name": dataset_json["name"],
        "description": dataset_json["description"],
        "file_url": dataset_json["url"],
        "number_of_samples": qualities_json["NumberOfInstances"],
        "number_of_features": qualities_json["NumberOfFeatures"],
        "number_of_classes": qualities_json.get("NumberOfClasses"),
    }
