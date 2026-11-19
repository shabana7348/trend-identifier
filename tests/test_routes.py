import pytest
from app.routes import app, get_dashboard_data


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"GitHub Technology Trend Identifier" in response.data


def test_results_page_loads(client):
    response = client.get("/results")
    assert response.status_code == 200
    assert b"Fastest-Growing Programming Languages" in response.data
    assert b"django/django" in response.data


def test_get_dashboard_data_returns_trends():
    language_trends, repo_trends = get_dashboard_data()
    assert len(language_trends) > 0
    assert len(repo_trends) > 0
    assert language_trends[0]["language"] == "Python"


def test_results_handles_missing_file(client, monkeypatch):
    monkeypatch.setattr("app.routes.SAMPLE_CSV", "does_not_exist.csv")
    response = client.get("/results")
    assert response.status_code == 200
    assert b"Error:" in response.data
