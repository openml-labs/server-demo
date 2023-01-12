import pathlib


def test_resources_path() -> pathlib.Path:
    """Return the absolute path of src/tests/resources"""
    return pathlib.Path(__file__).parent.parent / "resources"
