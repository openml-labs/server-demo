from sqlalchemy.orm import Session

from database.models import Publication, Dataset


def test_happy_path(engine, client):
    datasets = [Dataset(name="dset1", platform="openml", platform_specific_identifier="1"),
                Dataset(name="dset1", platform="other_platform", platform_specific_identifier="1"),
                ]
    publications = [Publication(title="Title 1", url="https://test.test", datasets=datasets),
                    Publication(title="Title 2", url="https://test.test2", datasets=datasets)]
    with Session(engine) as session:
        session.add_all(datasets)
        session.add_all(publications)
        session.commit()

    response = client.get("/publication/1")
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['title'] == 'Title 1'
    assert response_json['url'] == 'https://test.test'
    assert response_json['id'] == 1
    assert len(response_json['datasets']) == len(datasets)
    assert len(response_json) == 4


def test_publication_not_found(engine, client):
    publications = [Publication(title="Title 1", url="https://test.test", datasets=[])]
    with Session(engine) as session:
        session.add_all(publications)
        session.commit()
    response = client.get("/publication/2")  # Note that only publication 1 exists
    assert response.status_code == 404
    assert response.json()['detail'] == "Publication '2' not found in the database."
