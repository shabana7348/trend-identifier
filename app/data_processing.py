
import csv
import os

from app.exceptions import DataValidationError


# =========================================================
# PART 1: ORIGINAL DATA PROCESSING
# =========================================================

REQUIRED_COLUMNS = [
    "repo_name", "language", "stars",
    "created_at", "updated_at", "collected_on",
]


def load_raw_data(path):
    """Open a raw CSV file, check it, and return a list of rows."""
    if not str(path).lower().endswith(".csv"):
        raise DataValidationError("File must be a .csv file")

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            rows = list(reader)
    except FileNotFoundError:
        raise DataValidationError(f"File not found: {path}")

    if not columns:
        raise DataValidationError("The file is empty")

    missing = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing:
        raise DataValidationError(f"Missing columns: {missing}")

    return rows


def clean_data(rows):
    """Remove duplicates and bad rows, and fix missing values."""
    cleaned = []
    seen = set()

    for row in rows:
        repo = (row.get("repo_name") or "").strip()
        date = (row.get("collected_on") or "").strip()

        if not repo:
            continue

        if (repo, date) in seen:
            continue

        try:
            stars = int(row.get("stars"))
        except (ValueError, TypeError):
            continue

        if stars < 0:
            continue

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


CATEGORIES = {
    "python": "Data/AI",
    "r": "Data/AI",
    "jupyter notebook": "Data/AI",
    "javascript": "Web",
    "typescript": "Web",
    "html": "Web",
    "css": "Web",
    "php": "Web",
    "java": "Backend",
    "c#": "Backend",
    "ruby": "Backend",
    "kotlin": "Mobile",
    "swift": "Mobile",
    "dart": "Mobile",
    "rust": "Systems",
    "go": "Systems",
    "c": "Systems",
    "c++": "Systems",
}


def categorise_technology(language):
    """Return the group for a programming language, or 'Other'."""
    key = (language or "").strip().lower()
    return CATEGORIES.get(key, "Other")


PROCESSED_COLUMNS = [
    "repo_name", "language", "category", "stars",
    "created_at", "updated_at", "collected_on",
]


def process_and_save(raw_path, output_folder="data/processed"):
    """Load, clean and categorise a raw CSV, then save the result."""
    rows = clean_data(load_raw_data(raw_path))

    for row in rows:
        row["category"] = categorise_technology(row["language"])

    os.makedirs(output_folder, exist_ok=True)

    file_name = "processed_" + os.path.basename(str(raw_path))
    output_path = os.path.join(output_folder, file_name)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=PROCESSED_COLUMNS,
            extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    return output_path


# =========================================================
# PART 2: TECHNOLOGY SNAPSHOT PROCESSING
# =========================================================

SNAPSHOT_REQUIRED_COLUMNS = [
    "collected_on",
    "technology",
    "full_name",
    "language",
    "stars",
    "topics",
]


SNAPSHOT_PROCESSED_COLUMNS = [
    "collected_on",
    "technology",
    "repo_name",
    "language",
    "category",
    "stars",
    "topics",
]


# Technology-to-domain mapping
TECHNOLOGY_DOMAINS = {
    # Web
    "react": "Web",
    "nextjs": "Web",
    "next.js": "Web",
    "vue": "Web",
    "angular": "Web",
    "svelte": "Web",
    "nodejs": "Web",
    "node.js": "Web",
    "express": "Web",
    "typescript": "Web",
    "javascript": "Web",

    # AI
    "tensorflow": "AI",
    "pytorch": "AI",
    "keras": "AI",
    "langchain": "AI",
    "llm": "AI",
    "machine-learning": "AI",
    "deep-learning": "AI",
    "generative-ai": "AI",

    # Mobile
    "flutter": "Mobile",
    "react-native": "Mobile",
    "android": "Mobile",
    "ios": "Mobile",
    "kotlin": "Mobile",
    "swift": "Mobile",

    # Cybersecurity
    "cybersecurity": "Cybersecurity",
    "penetration-testing": "Cybersecurity",
    "osint": "Cybersecurity",
    "owasp": "Cybersecurity",
    "vulnerability-scanner": "Cybersecurity",
    "metasploit": "Cybersecurity",

    # Cloud
    "docker": "Cloud",
    "kubernetes": "Cloud",
    "aws": "Cloud",
    "azure": "Cloud",
    "terraform": "Cloud",
    "devops": "Cloud",

    # AR/VR
    "unity": "AR/VR",
    "unreal-engine": "AR/VR",
    "ar": "AR/VR",
    "vr": "AR/VR",
    "augmented-reality": "AR/VR",
    "virtual-reality": "AR/VR",

    # Blockchain
    "blockchain": "Blockchain",
    "ethereum": "Blockchain",
    "web3": "Blockchain",
    "solidity": "Blockchain",

    # Data Science
    "data-science": "Data Science",
    "pandas": "Data Science",
    "numpy": "Data Science",
    "scikit-learn": "Data Science",
    "jupyter": "Data Science",

    # Internet of Things
    "iot": "IoT",
    "raspberry-pi": "IoT",
    "arduino": "IoT",
    "embedded-systems": "IoT",
}


def categorise_domain(technology):
    """Return the domain of a technology, or 'Other'."""
    key = (technology or "").strip().lower()
    return TECHNOLOGY_DOMAINS.get(key, "Other")


def load_snapshot(path):
    """Load and validate a GitHub technology snapshot CSV."""
    if not str(path).lower().endswith(".csv"):
        raise DataValidationError("File must be a .csv file")

    try:
        # utf-8-sig handles hidden BOM characters at the start of CSV files.
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            rows = list(reader)
    except FileNotFoundError:
        raise DataValidationError(f"File not found: {path}")

    if not columns:
        raise DataValidationError("The file is empty")

    missing = [
        col for col in SNAPSHOT_REQUIRED_COLUMNS
        if col not in columns
    ]

    if missing:
        raise DataValidationError(f"Missing columns: {missing}")

    return rows


def clean_snapshot(rows):
    """Clean snapshot rows and remove invalid or duplicate entries."""
    cleaned = []
    seen = set()

    for row in rows:
        technology = (row.get("technology") or "").strip().lower()
        repo = (row.get("full_name") or "").strip()
        date = (row.get("collected_on") or "").strip()

        if not technology or not repo:
            continue

        # Same repository can belong to different technologies.
        # Keep separate records for different collection dates.
        duplicate_key = (technology, repo, date)

        if duplicate_key in seen:
            continue

        try:
            stars = int(row.get("stars"))
        except (ValueError, TypeError):
            continue

        if stars < 0:
            continue

        language = (row.get("language") or "").strip()
        if not language:
            language = "Unknown"

        new_row = {
            "collected_on": date,
            "technology": technology,
            "repo_name": repo,
            "language": language,
            "category": categorise_domain(technology),
            "stars": stars,
            "topics": (row.get("topics") or "").strip(),
        }

        seen.add(duplicate_key)
        cleaned.append(new_row)

    return cleaned


def process_snapshot(raw_path, output_folder="data/processed"):
    """Clean a snapshot CSV, save it, and return the output path."""
    rows = clean_snapshot(load_snapshot(raw_path))

    os.makedirs(output_folder, exist_ok=True)

    file_name = "processed_" + os.path.basename(str(raw_path))
    output_path = os.path.join(output_folder, file_name)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=SNAPSHOT_PROCESSED_COLUMNS,
            extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    return output_path
