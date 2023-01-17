from sqlalchemy import Engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from database.models import Publication


def test_happy_path(client: TestClient, engine: Engine):
    publications = [
        Publication(title="Title 1", url="https://test.test"),
        Publication(title="Title 2", url="https://test.test2"),
    ]
    with Session(engine) as session:
        # Populate database
        session.add_all(publications)
        session.commit()

    response = client.get("/publications")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert {pub["title"] for pub in response_json} == {"Title 1", "Title 2"}
    assert {pub["url"] for pub in response_json} == {"https://test.test", "https://test.test2"}
    assert {pub["id"] for pub in response_json} == {1, 2}
    for pub in response_json:
        assert len(pub) == 3
