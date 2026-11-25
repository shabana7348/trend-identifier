import csv
import os
from pathlib import Path
import requests
from datetime import date
import time

from app.exceptions import DataCollectionError
from app.topics import ALL_TOPICS

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
    

def collect_data(languages, count, path):
    """Fetch repos for several languages and save them in one CSV."""
    if not languages:
        raise DataCollectionError("Give at least one language")

    # 1. Collect repos for every language
    rows = []
    for language in languages:
        rows.extend(fetch_repositories(language, count))

    # 2. Make sure the folder exists, then save
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    save_to_csv(rows, path)
    return rows


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
SNAPSHOT_COLUMNS = ["collected_on", "technology", "full_name", "language", "stars", "topics"]


def fetch_topic_repos(topic, token=None, per_page=30, session=None):
    """Return the most-starred repos for one GitHub topic as a list of dicts."""
    http = session or requests
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {"q": f"topic:{topic}", "sort": "stars", "order": "desc", "per_page": per_page}

    response = http.get(GITHUB_SEARCH_URL, headers=headers, params=params, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"GitHub returned {response.status_code} for topic '{topic}'")

    today = date.today().isoformat()
    return [
        {
            "collected_on": today,
            "technology": topic,
            "full_name": item["full_name"],
            "language": item.get("language") or "",
            "stars": item["stargazers_count"],
            "topics": ";".join(item.get("topics", [])),
        }
        for item in response.json().get("items", [])
    ]


def collect_snapshot(topics=None, token=None, per_page=30, pause=None, session=None):
    """Collect repos for every topic. Topics that fail are skipped, not fatal."""
    token = token or os.environ.get("GITHUB_TOKEN")
    if pause is None:
        pause = 2 if token else 6  # unauthenticated search is limited to ~10 requests/min

    rows, failed = [], []
    for topic in topics or ALL_TOPICS:
        try:
            rows.extend(fetch_topic_repos(topic, token, per_page, session))
        except (RuntimeError, requests.RequestException):
            failed.append(topic)
        time.sleep(pause)
    if failed:
        print(f"Skipped topics: {failed}")
    return rows


def save_snapshot(rows, directory="data/raw", today=None):
    """Write one dated CSV per day: data/raw/snapshot_YYYY-MM-DD.csv"""
    if not rows:
        raise ValueError("No rows to save.")
    today = today or date.today().isoformat()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"snapshot_{today}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SNAPSHOT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


if __name__ == "__main__":
    snapshot_rows = collect_snapshot()
    if not snapshot_rows:
        raise SystemExit("GitHub returned no repositories; no snapshot was saved.")
    print(f"Saved {len(snapshot_rows)} live GitHub repositories to {save_snapshot(snapshot_rows)}")
