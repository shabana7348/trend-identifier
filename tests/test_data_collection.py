
import csv
from unittest.mock import MagicMock

import pytest
import requests

from app import data_collection
from app.data_collection import (
    collect_data,
    collect_snapshot,
    fetch_repositories,
    fetch_topic_repos,
    save_snapshot,
    save_to_csv,
)
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


def _response(status=200, items=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = {"items": items or []}
    return r


ITEM = {"full_name": "facebook/react", "language": "JavaScript",
        "stargazers_count": 200000, "topics": ["react", "frontend"]}


def test_fetch_topic_repos_returns_rows():
    session = MagicMock()
    session.get.return_value = _response(items=[ITEM])
    rows = fetch_topic_repos("react", session=session)
    assert rows[0]["technology"] == "react"
    assert rows[0]["stars"] == 200000
    assert rows[0]["topics"] == "react;frontend"


def test_fetch_topic_repos_missing_language_becomes_empty():
    session = MagicMock()
    session.get.return_value = _response(items=[{**ITEM, "language": None}])
    assert fetch_topic_repos("react", session=session)[0]["language"] == ""


def test_fetch_topic_repos_bad_status_raises():
    session = MagicMock()
    session.get.return_value = _response(status=403)
    with pytest.raises(RuntimeError):
        fetch_topic_repos("react", session=session)


def test_collect_snapshot_skips_failed_topics():
    session = MagicMock()
    session.get.side_effect = [_response(items=[ITEM]), _response(status=500)]
    rows = collect_snapshot(topics=["react", "vue"], pause=0, session=session)
    assert len(rows) == 1


def test_save_snapshot_writes_dated_file(tmp_path):
    rows = [{"collected_on": "2026-11-24", "technology": "react", "full_name": "a/b",
             "language": "JS", "stars": 5, "topics": "react"}]
    path = save_snapshot(rows, directory=str(tmp_path), today="2026-11-24")
    assert path.endswith("snapshot_2026-11-24.csv")
    with open(path, newline="", encoding="utf-8") as f:
        assert list(csv.DictReader(f))[0]["technology"] == "react"


def test_save_snapshot_empty_raises(tmp_path):
    with pytest.raises(ValueError):
        save_snapshot([], directory=str(tmp_path))