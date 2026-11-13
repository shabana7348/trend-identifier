# trend-identifier
Emerging Technology and Trends Identifier
## Data Collection

The app collects popular repositories from the GitHub Search API.

To create the raw data file, run this from the project folder:

    python -c "from app.data_collection import collect_data; collect_data(['Python', 'JavaScript', 'Go', 'Rust'], 20, 'data/raw_data.csv')"

This creates `data/raw_data.csv` with these columns:
repo_name, language, stars, created_at, updated_at, collected_on

Limitations:
- GitHub allows only a limited number of unauthenticated searches per minute. If you see a rate limit error, wait one minute and try again.
- Each search returns at most 100 repositories.