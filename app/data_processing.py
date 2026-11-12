import csv

from app.exceptions import DataValidationError

# The columns every raw CSV file must have
REQUIRED_COLUMNS = [
    "repo_name", "language", "stars",
    "created_at", "updated_at", "collected_on",
]


def load_raw_data(path):
    """Open a raw CSV file, check it, and return a list of rows."""
    # 1. The file must end with .csv
    if not str(path).lower().endswith(".csv"):
        raise DataValidationError("File must be a .csv file")

    # 2. Try to open the file
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            rows = list(reader)
    except FileNotFoundError:
        raise DataValidationError(f"File not found: {path}")

    # 3. An empty file has no column names
    if not columns:
        raise DataValidationError("The file is empty")

    # 4. Check that all the needed columns exist
    missing = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing:
        raise DataValidationError(f"Missing columns: {missing}")

    return rows