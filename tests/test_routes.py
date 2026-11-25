import pandas as pd
import pytest

import app.routes as routes
from app.exceptions import DataValidationError

TECH = pd.DataFrame({
    "collected_on": ["2026-11-01", "2026-11-08", "2026-11-01", "2026-11-08"],
    "technology": ["react", "react", "vue", "vue"],
    "full_name": ["a/x", "a/x", "b/z", "b/z"],
    "stars": [100, 110, 50, 60],
})
LANG = pd.DataFrame({
    "collected_on": ["2026-11-01", "2026-11-08", "2026-11-01", "2026-11-08"],
    "repo_name": ["a/x", "a/x", "b/z", "b/z"],
    "language": ["Python", "Python", "Go", "Go"],
    "stars": [100, 110, 50, 60],
})


@pytest.fixture
def client(monkeypatch):
    routes.app.config["TESTING"] = True
    monkeypatch.setattr(routes, "load_technology_data", lambda: TECH.copy())
    monkeypatch.setattr(routes, "load_language_data", lambda: LANG.copy())
    return routes.app.test_client()


def _no_data():
    raise DataValidationError("No data yet.")


def test_index_shows_growth_and_popularity(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Top growing technologies" in resp.data
    assert b"vue" in resp.data


def test_index_without_data_still_loads(client, monkeypatch):
    monkeypatch.setattr(routes, "load_technology_data", _no_data)
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"No data yet." in resp.data


def test_index_single_snapshot_shows_growth_message(client, monkeypatch):
    one_day = TECH[TECH["collected_on"] == "2026-11-01"]
    monkeypatch.setattr(routes, "load_technology_data", lambda: one_day.copy())
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"two or more dates" in resp.data


def test_results_page(client):
    resp = client.get("/results")
    assert resp.status_code == 200
    assert b"Python" in resp.data


def test_results_without_data_shows_error(client, monkeypatch):
    monkeypatch.setattr(routes, "load_language_data", _no_data)
    resp = client.get("/results")
    assert resp.status_code == 200
    assert b"No data yet." in resp.data


def test_advisor_get(client):
    assert client.get("/advisor").status_code == 200


def test_advisor_post_recommends(client):
    resp = client.post("/advisor", data={"description": "a simple website for beginners"})
    assert resp.status_code == 200
    assert b"Best match" in resp.data


def test_advisor_empty_description_shows_error(client):
    resp = client.post("/advisor", data={"description": "  "})
    assert b"Please describe your project" in resp.data


def test_advisor_without_data_shows_error(client, monkeypatch):
    monkeypatch.setattr(routes, "load_technology_data", _no_data)
    resp = client.post("/advisor", data={"description": "website"})
    assert b"No data yet." in resp.data


def test_api_top(client):
    data = client.get("/api/top").get_json()
    assert data[0]["technology"] == "react"
    assert data[0]["total_stars"] == 110


def test_api_trends_returns_series(client):
    data = client.get("/api/trends?tech=react").get_json()
    assert data["react"] == [
        {"date": "2026-11-01", "stars": 100},
        {"date": "2026-11-08", "stars": 110},
    ]


def test_api_trends_requires_tech(client):
    assert client.get("/api/trends").status_code == 400