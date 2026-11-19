from pathlib import Path

import pandas as pd
import pytest

from app.exceptions import AnalysisError
from app.analyzer import calculate_language_trends, calculate_repo_trends

SAMPLE = Path(__file__).parent / "sample_data" / "clean_sample.csv"


def test_top_language_is_python():
    df = pd.read_csv(SAMPLE)
    result = calculate_language_trends(df)
    assert result.iloc[0]["language"] == "Python"


def test_python_growth_is_500():
    df = pd.read_csv(SAMPLE)
    result = calculate_language_trends(df)
    python_row = result[result["language"] == "Python"].iloc[0]
    assert python_row["growth"] == 500


def test_repo_seen_once_is_ignored():
    df = pd.read_csv(SAMPLE)
    result = calculate_language_trends(df)
    assert "Go" not in list(result["language"])


def test_empty_data():
    with pytest.raises(AnalysisError):
        calculate_language_trends(pd.DataFrame())


def test_missing_column():
    df = pd.DataFrame({"repo_name": ["flask"], "stars": [100]})
    with pytest.raises(AnalysisError):
        calculate_language_trends(df)

def test_top_repo_is_django():
    df = pd.read_csv(SAMPLE)
    result = calculate_repo_trends(df)
    assert result.iloc[0]["repo_name"] == "django/django"
    assert result.iloc[0]["growth"] == 500


def test_only_repos_seen_twice_are_included():
    df = pd.read_csv(SAMPLE)
    result = calculate_repo_trends(df)
    assert len(result) == 3
    assert "golang/go" not in list(result["repo_name"])


def test_top_n_limits_results():
    df = pd.read_csv(SAMPLE)
    result = calculate_repo_trends(df, top_n=2)
    assert len(result) == 2


def test_repo_trends_empty_data():
    with pytest.raises(AnalysisError):
        calculate_repo_trends(pd.DataFrame())


def test_repo_trends_missing_column():
    df = pd.DataFrame({"repo_name": ["flask"], "stars": [100]})
    with pytest.raises(AnalysisError):
        calculate_repo_trends(df)       