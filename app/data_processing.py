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

def clean_data(rows):
    """Remove duplicates and bad rows, and fix missing values."""
    cleaned = []
    seen = set()  # remembers (repo, date) pairs we already kept

    for row in rows:
        repo = (row.get("repo_name") or "").strip()
        date = (row.get("collected_on") or "").strip()

        # Skip rows with no repo name
        if not repo:
            continue

        # Skip duplicates: same repo on the same day
        if (repo, date) in seen:
            continue

        # Stars must be a number that is not negative
        try:
            stars = int(row.get("stars"))
        except (ValueError, TypeError):
            continue
        if stars < 0:
            continue

        # A missing language becomes "Unknown"
        language = (row.get("language") or "").strip()
        if not language:
            language = "Unknown"

        new_row = dict(row)
        new_row["repo_name"] = repo
        new_row["language"] = language
        new_row["stars"] = stars

        seen.add((repo, date))
        cleaned.append(new_row)

    return cleaned