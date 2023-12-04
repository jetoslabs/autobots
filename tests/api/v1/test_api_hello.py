from fastapi.testclient import TestClient

from conftest import test_client


def test_hello_happy_path(test_client: TestClient):
    response = test_client.get("/v1/hello")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}
