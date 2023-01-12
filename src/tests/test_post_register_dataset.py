from sqlalchemy.orm import Session

from database.models import Dataset


def test_happy_path(engine, client):
    datasets = [Dataset(name="dset1", platform="openml", platform_specific_identifier="1"),
                Dataset(name="dset1", platform="other_platform", platform_specific_identifier="1"),
                Dataset(name="dset2", platform="other_platform", platform_specific_identifier="2"),
                ]
    with Session(engine) as session:
        session.add_all(datasets)
        session.commit()

    response = client.post("/register/dataset", json={
        "name": "dset2", "platform": "openml", "platform_identifier": "2"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "dset2"
    assert response_json["platform"] == "openml"
    assert response_json["platform_specific_identifier"] == "2"
    assert response_json["id"] == 4
    assert response_json["publications"] == []
    assert len(response_json) == 5


def test_unicode(engine, client):
    name = "По 123 oživlënnym Ἰοὺ ἰού कृच्छ्राद् 子曰رَّحْمـَبنِ"
    response = client.post("/register/dataset", json={
        "name": name, "platform": "openml", "platform_identifier": "2"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == name


def test_duplicated_dataset(engine, client):
    datasets = [Dataset(name="dset1", platform="openml", platform_specific_identifier="1")]
    with Session(engine) as session:
        session.add_all(datasets)
        session.commit()
    response = client.post("/register/dataset", json={
        "name": "dset1", "platform": "openml", "platform_identifier": "1"
    })
    assert response.status_code == 409
    assert response.json()['detail'] == "Duplicate entry."
