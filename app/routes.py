import pandas as pd
from flask import jsonify, render_template, request

from app.analyzer import technology_growth, top_growing, trend_series
from app.exceptions import AnalysisError, DataValidationError
from app.recommender import recommend

PROCESSED_PATH = "data/processed/technologies.csv"


def load_processed():
    return pd.read_csv(PROCESSED_PATH)


@bp.route("/advisor", methods=["GET", "POST"])
def advisor():
    description = request.form.get("description", "").strip()
    result, error = None, None
    if request.method == "POST":
        try:
            if not description:
                raise DataValidationError("Please describe your project.")
            result = recommend(description, technology_growth(load_processed()))
        except FileNotFoundError:
            error = "No processed data yet. Run the data pipeline first."
        except (DataValidationError, AnalysisError) as exc:
            error = str(exc)
    return render_template("advisor.html", description=description, result=result, error=error)


@bp.route("/api/top")
def api_top():
    try:
        return jsonify(top_growing(load_processed(), n=5).to_dict("records"))
    except FileNotFoundError:
        return jsonify({"error": "No processed data yet."}), 404
    except (DataValidationError, AnalysisError) as exc:
        return jsonify({"error": str(exc)}), 400


@bp.route("/api/trends")
def api_trends():
    techs = request.args.getlist("tech")
    if not techs:
        return jsonify({"error": "Provide at least one ?tech=name"}), 400
    try:
        df = load_processed()
    except FileNotFoundError:
        return jsonify({"error": "No processed data yet."}), 404
    return jsonify({t.lower(): trend_series(df, t) for t in techs})