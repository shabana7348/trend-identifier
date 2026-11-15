from pathlib import Path
from flask import Flask, render_template

# Tell Flask where the 'templates' and 'static' folders live
BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@app.route("/")
def index():
    """Home page of the dashboard."""
    return render_template("index.html")


@app.route("/results")
def results():
    """Results page showing trending languages and charts."""
    # Fake demo data until Nividhini's analyzer.py is finished
    demo_trends = [
        {"language": "Python", "repos": 3, "total_stars": 148505, "growth": 18.5},
        {"language": "JavaScript", "repos": 2, "total_stars": 437400, "growth": 12.2},
        {"language": "Rust", "repos": 1, "total_stars": 98300, "growth": 24.0},
        {"language": "Go", "repos": 1, "total_stars": 125000, "growth": 9.8},
    ]
    return render_template("results.html", trends=demo_trends)
