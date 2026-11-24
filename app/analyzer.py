import pandas as pd

from app.exceptions import AnalysisError

# The columns the cleaned data must have
NEEDED_COLUMNS = ["repo_name", "language", "stars", "collected_on"]


def calculate_language_trends(df):
    """Find which languages are growing fastest in stars."""
    # 1. Stop early if there is no data
    if df.empty:
        raise AnalysisError("No data to analyse")

    # 2. Check that the columns we need are there
    missing = [col for col in NEEDED_COLUMNS if col not in df.columns]
    if missing:
        raise AnalysisError(f"Missing columns: {missing}")

    # 3. Put the rows in date order (oldest first)
    df = df.sort_values("collected_on")

    # 4. For each repo, find its first and last star count
    per_repo = df.groupby("repo_name").agg(
        language=("language", "first"),
        first_stars=("stars", "first"),
        last_stars=("stars", "last"),
        snapshots=("collected_on", "nunique"),
    )

    # 5. Keep only repos seen on 2 or more dates (we need two to measure growth)
    per_repo = per_repo[per_repo["snapshots"] >= 2].copy()

    # 6. Growth = newest stars minus oldest stars
    per_repo["growth"] = per_repo["last_stars"] - per_repo["first_stars"]

    # 7. Add up the numbers for each language
    by_language = per_repo.groupby("language").agg(
        repos=("growth", "count"),
        starting_stars=("first_stars", "sum"),
        growth=("growth", "sum"),
    ).reset_index()

    # 8. Growth as a percentage, rounded to 2 decimals
    by_language["growth_percent"] = (
    by_language["growth"] / by_language["starting_stars"].replace(0, pd.NA) * 100
    ).astype(float).round(2).fillna(0)

    # 9. Fastest-growing language first
    return by_language.sort_values("growth_percent", ascending=False).reset_index(drop=True)

def calculate_repo_trends(df, top_n=5):
        """Find the individual repos that gained the most stars."""
        # 1. Stop early if there is no data
        if df.empty:
            raise AnalysisError("No data to analyse")

        # 2. Check that the columns we need are there
        missing = [col for col in NEEDED_COLUMNS if col not in df.columns]
        if missing:
            raise AnalysisError(f"Missing columns: {missing}")

        # 3. Put the rows in date order (oldest first)
        df = df.sort_values("collected_on")

        # 4. For each repo, find its first and last star count
        per_repo = df.groupby("repo_name").agg(
            language=("language", "first"),
            first_stars=("stars", "first"),
            last_stars=("stars", "last"),
            snapshots=("collected_on", "nunique"),
        )

        # 5. Keep only repos seen on 2 or more dates
        per_repo = per_repo[per_repo["snapshots"] >= 2].copy()

        # 6. Growth = newest stars minus oldest stars
        per_repo["growth"] = per_repo["last_stars"] - per_repo["first_stars"]

        # 7. Growth as a percentage, rounded to 2 decimals
        per_repo["growth_percent"] = (
            per_repo["growth"] / per_repo["first_stars"] * 100
        ).round(2)

        # 8. Biggest growth first, keep only the top few repos
        per_repo = per_repo.reset_index().sort_values("growth", ascending=False)
        top = per_repo.head(top_n)

        # 9. Return only the columns we want, in a clear order
        return top[
            ["repo_name", "language", "first_stars", "last_stars", "growth", "growth_percent"]
        ].reset_index(drop=True)
 # ---- Trend status settings (adjust after you see real numbers) ----
RISING_THRESHOLD = 2.0       # growth % at or above this = Rising
DECLINING_THRESHOLD = -0.5   # growth % at or below this = Declining


def get_trend_status(growth_percent):
    """Turn a growth percentage into a label."""
    if growth_percent >= RISING_THRESHOLD:
        return "Rising"
    if growth_percent <= DECLINING_THRESHOLD:
        return "Declining"
    return "Stable"


def top_growing_languages(df, top_n=5):
    """Top languages by growth %, each with a trend status.
    Feeds the 'Top 5 growing' card on the homepage."""
    trends = calculate_language_trends(df).head(top_n).copy()
    trends["status"] = trends["growth_percent"].apply(get_trend_status)
    return trends.to_dict(orient="records")


def compare_languages(df, lang_a, lang_b):
    """Compare two languages side by side (for the Compare page)."""
    trends = calculate_language_trends(df)
    trends["key"] = trends["language"].str.lower()

    result = {}
    for name in (lang_a, lang_b):
        row = trends[trends["key"] == name.lower()]
        if row.empty:
            raise AnalysisError(f"No trend data found for '{name}'")
        row = row.iloc[0]
        result[name] = {
            "language": row["language"],
            "repos": int(row["repos"]),
            "growth": int(row["growth"]),
            "growth_percent": float(row["growth_percent"]),
            "status": get_trend_status(row["growth_percent"]),
        }
    return result