import pandas as pd

from app.recommender import extract_tags, recommend

GROWTH = pd.DataFrame({"technology": ["react", "vue", "flutter"],
                       "growth_pct": [10.0, 5.0, 30.0]})
EMPTY = pd.DataFrame(columns=["technology", "growth_pct"])


def test_extract_tags_handles_plurals_and_case():
    assert extract_tags("A Website for BEGINNERS on phones") == {"web", "beginner", "mobile"}


def test_extract_tags_empty():
    assert extract_tags("") == set()
    assert extract_tags(None) == set()


def test_web_beginner_picks_react():
    result = recommend("I want a simple website for beginners", GROWTH)
    assert result["best"]["technology"] == "react"
    assert "10.0%" in result["best"]["reason"]
    assert len(result["runners_up"]) <= 2


def test_growth_breaks_ties():
    result = recommend("an app for my phone", GROWTH)
    assert result["best"]["technology"] == "flutter"


def test_unrecognised_text_has_no_best():
    result = recommend("xyz qwerty", GROWTH)
    assert result["best"] is None and result["message"]


def test_works_with_no_growth_data():
    result = recommend("a website for beginners", EMPTY)
    assert result["best"] is not None