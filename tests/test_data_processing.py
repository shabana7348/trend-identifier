from pathlib import Path

import pytest

from app.data_processing import clean_data, load_raw_data
from app.exceptions import DataValidationError

SAMPLE = Path(__file__).parent / "sample_data" / "raw_sample.csv"


def make_row(repo="a/b", language="Python", stars="100", date="2026-11-11"):
    """Build one fake row for testing."""
    return {
        "repo_name": repo, "language": language, "stars": stars,
        "created_at": "2020-01-01", "updated_at": "2026-11-01",
        "collected_on": date,
    }


# ---- tests for load_raw_data ----

def test_loads_sample_file():
    rows = load_raw_data(SAMPLE)
    assert len(rows) == 12
    assert "repo_name" in rows[0]


def test_wrong_file_type():
    with pytest.raises(DataValidationError):
        load_raw_data("data.txt")


def test_file_not_found():
    with pytest.raises(DataValidationError):
        load_raw_data("does_not_exist.csv")


def test_missing_column(tmp_path):
    bad_file = tmp_path / "bad.csv"
    bad_file.write_text("repo_name,stars\nflask,100\n")
    with pytest.raises(DataValidationError):
        load_raw_data(bad_file)


def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")
    with pytest.raises(DataValidationError):
        load_raw_data(empty_file)


# ---- tests for clean_data ----

def test_removes_duplicates():
    rows = [make_row("x/y"), make_row("x/y")]
    assert len(clean_data(rows)) == 1


def test_same_repo_on_different_days_is_kept():
    rows = [make_row("x/y", date="2026-11-11"), make_row("x/y", date="2026-11-12")]
    assert len(clean_data(rows)) == 2


def test_missing_language_becomes_unknown():
    result = clean_data([make_row(language="")])
    assert result[0]["language"] == "Unknown"


def test_negative_stars_removed():
    assert clean_data([make_row(stars="-5")]) == []


def test_non_numeric_stars_removed():
    assert clean_data([make_row(stars="abc"), make_row("c/d", stars="")]) == []


def test_stars_become_numbers():
    result = clean_data([make_row(stars="80000")])
    assert result[0]["stars"] == 80000


def test_empty_list():
    assert clean_data([]) == []


def test_sample_file_gives_ten_rows():
    result = clean_data(load_raw_data(SAMPLE))
    assert len(result) == 10