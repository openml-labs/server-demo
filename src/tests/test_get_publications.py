from sqlalchemy.orm import Session

from database.models import Publication


def test_happy_path(engine, client):
    publications = [Publication(title="Title 1", url="https://test.test"),
                    Publication(title="Title 2", url="https://test.test2")]
    with Session(engine) as session:
        session.add_all(publications)
        session.commit()

    response = client.get("/publications")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert {ds['title'] for ds in response_json} == {"Title 1", "Title 2"}
    assert {ds['url'] for ds in response_json} == {"https://test.test", "https://test.test2"}
    assert {ds['id'] for ds in response_json} == {1, 2}
    for ds in response_json:
        assert len(ds) == 3
