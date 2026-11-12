import csv
import requests
from datetime import date

from app.exceptions import DataCollectionError

# The web address of GitHub's search service
GITHUB_URL = "https://api.github.com/search/repositories"


def fetch_repositories(language, count=30):
    """Ask GitHub for the most-starred repos in one language."""
    # 1. Check the inputs are sensible
    if not language:
        raise DataCollectionError("Language cannot be empty")
    if count < 1 or count > 100:
        raise DataCollectionError("Count must be between 1 and 100")

    # 2. Tell GitHub what we want
    params = {
        "q": f"language:{language}",   # only this language
        "sort": "stars",               # most stars first
        "order": "desc",
        "per_page": count,             # how many results
    }

    # 3. Send the request (stop waiting after 10 seconds)
    try:
        response = requests.get(GITHUB_URL, params=params, timeout=10)
        response.raise_for_status()    # raises an error if GitHub says no
    except requests.RequestException as error:
        raise DataCollectionError(f"Could not reach GitHub: {error}")

    # 4. Pick out only the columns we need
    today = str(date.today())
    rows = []
    for item in response.json()["items"]:
        rows.append({
            "repo_name": item["full_name"],
            "language": item["language"],
            "stars": item["stargazers_count"],
            "created_at": item["created_at"][:10],
            "updated_at": item["updated_at"][:10],
            "collected_on": today,
        })
    return rows


# The columns Shabana's code expects, in this order
COLUMNS = [
    "repo_name", "language", "stars",
    "created_at", "updated_at", "collected_on",
]


def save_to_csv(rows, path):
    """Write the collected rows into a CSV file."""
    # 1. Check the inputs
    if not rows:
        raise DataCollectionError("No data to save")
    if not str(path).lower().endswith(".csv"):
        raise DataCollectionError("File must be a .csv file")

    # 2. Write the file
    try:
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()       # first line: column names
            writer.writerows(rows)     # then one line per repo
    except OSError as error:
        raise DataCollectionError(f"Could not save file: {error}")