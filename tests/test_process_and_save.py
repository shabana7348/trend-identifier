import csv
from pathlib import Path

import pytest

from app.data_processing import process_and_save
from app.exceptions import DataValidationError

SAMPLE = Path(__file__).parent / "sample_data" / "raw_sample.csv"


def read_rows(path):
    """Read a saved CSV file back into a list of rows."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_creates_processed_file(tmp_path):
    output = process_and_save(SAMPLE, tmp_path)
    assert Path(output).exists()
    assert Path(output).name == "processed_raw_sample.csv"


def test_saved_file_has_ten_rows_and_category_column(tmp_path):
    rows = read_rows(process_and_save(SAMPLE, tmp_path))
    assert len(rows) == 10
    assert "category" in rows[0]


def test_categories_are_filled_in(tmp_path):
    rows = read_rows(process_and_save(SAMPLE, tmp_path))
    by_repo = {row["repo_name"]: row for row in rows}
    assert by_repo["pallets/flask"]["category"] == "Data/AI"
    assert by_repo["someuser/mystery-tool"]["language"] == "Unknown"
    assert by_repo["someuser/mystery-tool"]["category"] == "Other"


def test_creates_missing_folder(tmp_path):
    folder = tmp_path / "new" / "folder"
    output = process_and_save(SAMPLE, folder)
    assert Path(output).exists()


def test_invalid_input_raises_error(tmp_path):
    with pytest.raises(DataValidationError):
        process_and_save("data.txt", tmp_path)