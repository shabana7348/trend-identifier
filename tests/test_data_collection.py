
import csv


import pytest
import requests

from app import data_collection
from app.data_collection import collect_data, fetch_repositories, save_to_csv
from app.exceptions import DataCollectionError


class FakeResponse:
    """A pretend answer from GitHub, so tests don't use the internet."""

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "items": [
                {
                    "full_name": "pallets/flask",
                    "language": "Python",
                    "stargazers_count": 68000,
                    "created_at": "2010-04-06T10:00:00Z",
                    "updated_at": "2026-11-09T08:30:00Z",
                }
            ]
        }


def test_fetch_returns_rows(monkeypatch):
    monkeypatch.setattr(
        data_collection.requests, "get", lambda *args, **kwargs: FakeResponse()
    )
    rows = fetch_repositories("Python", 1)
    assert len(rows) == 1
    assert rows[0]["repo_name"] == "pallets/flask"
    assert rows[0]["created_at"] == "2010-04-06"


def test_empty_language():
    with pytest.raises(DataCollectionError):
        fetch_repositories("")


def test_bad_count():
    with pytest.raises(DataCollectionError):
        fetch_repositories("Python", 500)


def test_github_unreachable(monkeypatch):
    def broken_get(*args, **kwargs):
        raise requests.RequestException("no internet")

    monkeypatch.setattr(data_collection.requests, "get", broken_get)
    with pytest.raises(DataCollectionError):
        fetch_repositories("Python", 1)


def test_save_to_csv(tmp_path):
    rows = [{
        "repo_name": "pallets/flask",
        "language": "Python",
        "stars": 68000,
        "created_at": "2010-04-06",
        "updated_at": "2026-11-09",
        "collected_on": "2026-11-13",
    }]
    out_file = tmp_path / "out.csv"
    save_to_csv(rows, out_file)

    with open(out_file, newline="", encoding="utf-8") as file:
        saved = list(csv.DictReader(file))
    assert len(saved) == 1
    assert saved[0]["repo_name"] == "pallets/flask"


def test_save_no_data(tmp_path):
    with pytest.raises(DataCollectionError):
        save_to_csv([], tmp_path / "out.csv")


def test_save_wrong_file_type(tmp_path):
    with pytest.raises(DataCollectionError):
        save_to_csv([{"repo_name": "x"}], tmp_path / "out.txt")



def test_collect_data_saves_file(monkeypatch, tmp_path):
    monkeypatch.setattr(
        data_collection.requests, "get", lambda *args, **kwargs: FakeResponse()
    )
    out_file = tmp_path / "data" / "raw.csv"
    rows = collect_data(["Python", "Go"], 1, out_file)

    assert len(rows) == 2          # 1 repo for each of the 2 languages
    assert out_file.exists()       # the file was really created


def test_collect_data_no_languages(tmp_path):
    with pytest.raises(DataCollectionError):
        collect_data([], 5, tmp_path / "raw.csv")