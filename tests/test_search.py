import pytest
from app.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_search_endpoint(client):
    response = client.get("/search?q=test")
    assert response.status_code == 200
    assert "results" in response.json