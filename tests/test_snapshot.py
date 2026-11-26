
import csv
from pathlib import Path

import pytest

from app.data_processing import (
    TECHNOLOGY_DOMAINS,
    categorise_domain,
    clean_snapshot,
    load_snapshot,
    process_snapshot,
)

from app.exceptions import DataValidationError


HEADER = "collected_on,technology,full_name,language,stars,topics\n"


def make_row(
    technology="react",
    repo="a/b",
    language="JavaScript",
    stars="100",
    date="2026-11-25",
    topics="web;ui",
):
    return {
        "collected_on": date,
        "technology": technology,
        "full_name": repo,
        "language": language,
        "stars": stars,
        "topics": topics,
    }


def write_snapshot(folder, lines, name="snapshot_test.csv"):
    path = Path(folder) / name
    path.write_text(HEADER + "".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------
# 1. LOAD SNAPSHOT TESTS
# --------------------------------------------------

def test_loads_snapshot(tmp_path):
    path = write_snapshot(
        tmp_path,
        "2026-11-25,react,user/repo,JavaScript,100,web\n",
    )

    rows = load_snapshot(path)

    assert len(rows) == 1
    assert rows[0]["technology"] == "react"


def test_hidden_character_at_start_is_ignored(tmp_path):
    path = tmp_path / "snapshot.csv"

    path.write_text(
        "\ufeff" + HEADER +
        "2026-11-25,react,user/repo,JavaScript,100,web\n",
        encoding="utf-8",
    )

    rows = load_snapshot(path)

    assert len(rows) == 1


def test_old_format_file_is_rejected(tmp_path):
    path = tmp_path / "old.csv"

    path.write_text(
        "technology,repository,stars\nreact,user/repo,100\n",
        encoding="utf-8",
    )

    with pytest.raises(DataValidationError):
        load_snapshot(path)


def test_wrong_file_type(tmp_path):
    path = tmp_path / "snapshot.txt"
    path.write_text("test")

    with pytest.raises(DataValidationError):
        load_snapshot(path)


def test_file_not_found(tmp_path):
    path = tmp_path / "missing.csv"

    with pytest.raises(DataValidationError):
        load_snapshot(path)


def test_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")

    with pytest.raises(DataValidationError):
        load_snapshot(path)


# --------------------------------------------------
# 2. CLEAN SNAPSHOT TESTS
# --------------------------------------------------

def test_same_repo_under_two_technologies_is_kept():
    rows = [
        make_row(technology="react"),
        make_row(technology="javascript"),
    ]

    cleaned = clean_snapshot(rows)

    assert len(cleaned) == 2


def test_real_duplicate_is_removed():
    rows = [
        make_row(),
        make_row(),
    ]

    cleaned = clean_snapshot(rows)

    assert len(cleaned) == 1


def test_same_repo_on_next_day_is_kept():
    rows = [
        make_row(date="2026-11-25"),
        make_row(date="2026-11-26"),
    ]

    cleaned = clean_snapshot(rows)

    assert len(cleaned) == 2


def test_missing_language_becomes_unknown():
    rows = [
        make_row(language="")
    ]

    cleaned = clean_snapshot(rows)

    assert cleaned[0]["language"] == "Unknown"


def test_bad_stars_are_removed():
    rows = [
        make_row(stars="100"),
        make_row(stars="-5"),
        make_row(stars="abc"),
    ]

    cleaned = clean_snapshot(rows)

    assert len(cleaned) == 1
    assert cleaned[0]["stars"] == 100


def test_missing_technology_or_repo_is_removed():
    rows = [
        make_row(technology=""),
        make_row(repo=""),
        make_row(),
    ]

    cleaned = clean_snapshot(rows)

    assert len(cleaned) == 1


def test_output_has_repo_name_category_and_number_stars():
    rows = [
        make_row(technology="react")
    ]

    cleaned = clean_snapshot(rows)

    assert "repo_name" in cleaned[0]
    assert "category" in cleaned[0]
    assert isinstance(cleaned[0]["stars"], int)


def test_empty_list():
    cleaned = clean_snapshot([])

    assert cleaned == []


# --------------------------------------------------
# 3. TECHNOLOGY DOMAIN TESTS
# --------------------------------------------------

def test_domains():
    assert categorise_domain("react") == "Web"
    assert categorise_domain("tensorflow") == "AI"
    assert categorise_domain("flutter") == "Mobile"
    assert categorise_domain("metasploit") == "Cybersecurity"
    assert categorise_domain("kubernetes") == "Cloud"
    assert categorise_domain("unity") == "AR/VR"
    assert categorise_domain("ethereum") == "Blockchain"
    assert categorise_domain("pandas") == "Data Science"
    assert categorise_domain("arduino") == "IoT"


def test_unknown_technology_is_other():
    assert categorise_domain("unknown-tool") == "Other"


def test_nine_domains_are_covered():
    expected_domains = {
        "Web", "AI", "Mobile", "Cybersecurity", "Cloud",
        "AR/VR", "Blockchain", "Data Science", "IoT"
    }
    assert set(TECHNOLOGY_DOMAINS.values()) == expected_domains

# --------------------------------------------------
# 4. PROCESS SNAPSHOT TESTS
# --------------------------------------------------

def test_process_snapshot_saves_clean_file(tmp_path):
    raw_folder = tmp_path / "raw"
    output_folder = tmp_path / "processed"

    raw_folder.mkdir()

    path = write_snapshot(
        raw_folder,
        "2026-11-25,react,user/repo,JavaScript,100,web\n"
        "2026-11-25,react,user/repo,JavaScript,100,web\n"
        "2026-11-25,flutter,user/app,Dart,200,mobile\n",
    )

    output_path = process_snapshot(path, output_folder)

    assert Path(output_path).exists()
    assert Path(output_path).name == "processed_snapshot_test.csv"
    with open(output_path, encoding="utf-8", newline="") as file:
        saved_rows = list(csv.DictReader(file))

    assert len(saved_rows) == 2


def test_process_snapshot_rejects_bad_file(tmp_path):
    path = tmp_path / "bad.txt"
    path.write_text("invalid")

    with pytest.raises(DataValidationError):
        process_snapshot(path, tmp_path / "processed")
