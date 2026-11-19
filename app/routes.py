from pathlib import Path
import pandas as pd
from flask import Flask, render_template

from app.data_processing import load_raw_data, clean_data
from app.analyzer import calculate_language_trends, calculate_repo_trends
from app.exceptions import DataValidationError, AnalysisError

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CSV = BASE_DIR / "tests" / "sample_data" / "raw_sample.csv"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


def get_dashboard_data(csv_path=SAMPLE_CSV):
    """Run Shabana's cleaning + Nividhini's trend calculations on a CSV file."""
    raw_rows = load_raw_data(csv_path)
    cleaned_rows = clean_data(raw_rows)
    df = pd.DataFrame(cleaned_rows)

    lang_df = calculate_language_trends(df)
    repo_df = calculate_repo_trends(df, top_n=5)

    return lang_df.to_dict(orient="records"), repo_df.to_dict(orient="records")


@app.route("/")
def index():
    """Home page of the dashboard."""
    return render_template("index.html")


@app.route("/results")
def results():
    """Results page showing real language trends and top growing repos."""
    try:
        language_trends, repo_trends = get_dashboard_data(SAMPLE_CSV)
        return render_template(
            "results.html",
            language_trends=language_trends,
            repo_trends=repo_trends,
            error=None,
        )
    except (DataValidationError, AnalysisError) as exc:
        return render_template(
            "results.html",
            language_trends=[],
            repo_trends=[],
            error=str(exc),
        )
