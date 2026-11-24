import pandas as pd
import pytest

import app.routes as routes
from app import create_app  # adjust to match your existing test setup

SAMPLE = pd.DataFrame({
    "collected_on": ["2026-11-01", "2026-11-08"],
    "technology": ["react", "react"],
    "domain": ["Web Development"] * 2,
    "full_name": ["a/x", "a/x"],
    "stars": [100, 110],
})


@pytest.fixture
def client(monkeypatch):
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    monkeypatch.setattr(routes, "load_processed", lambda: SAMPLE)
    return flask_app.test_client()


def test_advisor_get(client):
    assert client.get("/advisor").status_code == 200


def test_advisor_post_recommends(client):
    resp = client.post("/advisor", data={"description": "a simple website for beginners"})
    assert resp.status_code == 200
    assert b"react" in resp.data


def test_advisor_empty_description_shows_error(client):
    resp = client.post("/advisor", data={"description": "  "})
    assert b"Please describe your project" in resp.data


def test_advisor_without_data_shows_friendly_error(client, monkeypatch):
    def boom():
        raise FileNotFoundError
    monkeypatch.setattr(routes, "load_processed", boom)
    resp = client.post("/advisor", data={"description": "website"})
    assert b"No processed data yet" in resp.data


def test_api_trends_returns_series(client):
    data = client.get("/api/trends?tech=react").get_json()
    assert data["react"][0] == {"date": "2026-11-01", "stars": 100}


def test_api_trends_requires_tech(client):
    assert client.get("/api/trends").status_code == 400


def test_api_top_returns_list(client):
    data = client.get("/api/top").get_json()
    assert data[0]["technology"] == "react"