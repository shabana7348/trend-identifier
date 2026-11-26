import glob
import os

import pandas as pd
from flask import Flask, jsonify, render_template, request

from app.analyzer import (
    calculate_repo_trends,
    calculate_technology_trends,
    get_trend_status,
    technology_popularity,
    top_growing_languages,
)
from app.exceptions import AnalysisError, DataValidationError
from app.recommender import recommend
from app.topics import DOMAINS as TOPIC_DOMAINS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

TECH_COLUMNS = ["technology", "full_name", "stars", "collected_on"]
LANGUAGE_COLUMNS = ["repo_name", "language", "stars", "collected_on"]

DOMAINS = [
    {"name": "Web Development", "icon": "🌐"},
    {"name": "AI & Machine Learning", "icon": "🤖"},
    {"name": "Mobile Development", "icon": "📱"},
    {"name": "Cybersecurity", "icon": "🔒"},
    {"name": "Cloud & DevOps", "icon": "☁️"},
    {"name": "AR/VR", "icon": "🥽"},
    {"name": "Blockchain", "icon": "⛓️"},
    {"name": "Data Science", "icon": "📊"},
    {"name": "IoT", "icon": "📡"},
]

DOMAIN_SLUGS = ["web-development", "ai-machine-learning", "mobile-development",
                "cybersecurity", "cloud-devops", "ar-vr", "blockchain",
                "data-science", "iot"]
DOMAIN_TOPIC_GROUPS = ["Web", "AI", "Mobile", "Cyber", "Cloud", "AR/VR",
                       "Blockchain", "Data", "IoT"]
for domain, slug in zip(DOMAINS, DOMAIN_SLUGS):
    domain["slug"] = slug

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


# ---------- data loading ----------

def _read_matching(required):
    """Merge every CSV in data/raw that has all the required columns."""
    frames = []
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.csv"))):
        try:
            df = pd.read_csv(path)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            continue
        if set(required) <= set(df.columns):
            frames.append(df)
    if not frames:
        raise DataValidationError(
           
        )
    return pd.concat(frames, ignore_index=True)


def load_technology_data():
    df = _read_matching(TECH_COLUMNS)
    df["technology"] = df["technology"].astype(str).str.strip().str.lower()
    return df


def load_language_data():
    """Load language rows from the newest available dated technology snapshots."""
    frames = []
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.csv"))):
        try:
            df = pd.read_csv(path)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            continue
        if set(TECH_COLUMNS + ["language"]) <= set(df.columns):
            language_df = df[["full_name", "language", "stars", "collected_on"]].rename(
                columns={"full_name": "repo_name"}
            )
            frames.append(language_df)
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        return combined.drop_duplicates(["repo_name", "collected_on"], keep="last")
    return _read_matching(LANGUAGE_COLUMNS)


# ---------- analysis helpers (the only place that calls the analyzer) ----------

def get_top_technologies(df, n=5):
    return technology_popularity(df, top_n=n).to_dict("records")


def get_growing(df, n=5):
    """Top growing technologies, or [] while there is only one snapshot date."""
    try:
        trends = calculate_technology_trends(df)
    except AnalysisError:
        return []
    trends = trends.head(n).copy()
    trends["status"] = trends["growth_percent"].apply(get_trend_status)
    return trends.to_dict("records")


def get_zero_growth(df):
    """Technologies whose total star count did not change across snapshots."""
    try:
        trends = calculate_technology_trends(df)
    except AnalysisError:
        return []
    flat = trends[trends["growth"] == 0][["technology", "growth"]]
    return flat.to_dict("records")


def get_trends(df):
    """DataFrame with 'technology' and 'growth_pct' (empty while only one snapshot)."""
    try:
        trends = calculate_technology_trends(df)
    except AnalysisError:
        return pd.DataFrame(columns=["technology", "growth_pct"])
    return trends.rename(columns={"growth_percent": "growth_pct"})


def get_series(df, technology):
    """Total stars per snapshot date for one technology (for the chart)."""
    sub = df[df["technology"] == technology.strip().lower()]
    daily = sub.drop_duplicates(["collected_on", "full_name"]).groupby("collected_on")["stars"].sum().sort_index()
    return [{"date": str(d), "stars": int(s)} for d, s in daily.items()]


# ---------- pages ----------

@app.route("/")
def index():
    popular, growing, flat_growth, message = [], [], [], None
    try:
        df = load_technology_data()
        popular = get_top_technologies(df)
        growing = get_growing(df)
        flat_growth = get_zero_growth(df)
        if not growing:
            message = "Growth appears once there are snapshots from two or more dates."
    except (DataValidationError, AnalysisError) as exc:
        message = str(exc)
    return render_template("index.html", popular=popular, growing=growing,
                           flat_growth=flat_growth, message=message, domains=DOMAINS)


@app.route("/results")
def results():
    language_trends, repo_trends, error = [], [], None
    try:
        df = load_language_data()
        language_trends = top_growing_languages(df)
        repo_trends = calculate_repo_trends(df).to_dict("records")
    except (DataValidationError, AnalysisError) as exc:
        error = str(exc)
    return render_template("results.html", language_trends=language_trends,
                           repo_trends=repo_trends, source_name="data/raw", error=error)


@app.route("/domain/<domain_key>")
def domain_page(domain_key):
    try:
        domain_index = DOMAIN_SLUGS.index(domain_key)
    except ValueError:
        return "Domain not found", 404

    domain, error = DOMAINS[domain_index], None
    technologies = []
    try:
        df = load_technology_data()
        topics = TOPIC_DOMAINS[DOMAIN_TOPIC_GROUPS[domain_index]]
        domain_df = df[df["technology"].isin(topics)]
        if domain_df.empty:
            error = "No GitHub snapshot data is available for this domain yet."
        else:
            technologies = get_top_technologies(domain_df, n=len(topics))
    except (DataValidationError, AnalysisError) as exc:
        error = str(exc)
    return render_template("domain.html", domain=domain, technologies=technologies, error=error)


@app.route("/advisor", methods=["GET", "POST"])
def advisor():
    description = request.form.get("description", "").strip()
    result, error = None, None
    if request.method == "POST":
        try:
            if not description:
                raise DataValidationError("Please describe your project.")
            result = recommend(description, get_trends(load_technology_data()))
        except (DataValidationError, AnalysisError) as exc:
            error = str(exc)
    return render_template("advisor.html", description=description, result=result, error=error)


# ---------- JSON for the charts ----------

@app.route("/api/top")
def api_top():
    try:
        return jsonify(get_top_technologies(load_technology_data()))
    except (DataValidationError, AnalysisError) as exc:
        return jsonify({"error": str(exc)}), 404


@app.route("/api/trends")
def api_trends():
    techs = request.args.getlist("tech")
    if not techs:
        return jsonify({"error": "Provide at least one ?tech=name"}), 400
    try:
        df = load_technology_data()
    except DataValidationError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify({t.lower(): get_series(df, t) for t in techs})
