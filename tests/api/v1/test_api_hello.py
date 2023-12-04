from fastapi.testclient import TestClient

from autobots.main import app


def test_hello_happy_path():
    client = TestClient(app)
    response = client.get("/v1/hello")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}