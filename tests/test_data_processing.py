from pathlib import Path

import pytest

from app.data_processing import load_raw_data
from app.exceptions import DataValidationError

SAMPLE = Path(__file__).parent / "sample_data" / "raw_sample.csv"


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
