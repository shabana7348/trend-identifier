from pathlib import Path

import pandas as pd
import pytest

from app.exceptions import AnalysisError
from app.analyzer import calculate_language_trends

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