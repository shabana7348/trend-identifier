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

## Data Processing (Member 2: Shabana)

**File:** `app/data_processing.py`

This module cleans the raw GitHub data collected by `data_collection.py` so the trend analysis can trust the numbers.

| Function | What it does |
|---|---|
| `load_raw_data(path)` | Opens a raw CSV, checks the file type and required columns, and returns a list of rows |
| `clean_data(rows)` | Removes duplicate repos (same repo, same day), drops rows with negative or non-numeric stars, and fills a missing language with `Unknown` |
| `categorise_technology(language)` | Groups a language into Data/AI, Web, Backend, Mobile, Systems, or Other |
| `process_and_save(raw_path)` | Runs the three steps above and saves the result to `data/processed/` |

**Processed CSV columns:** `repo_name, language, category, stars, created_at, updated_at, collected_on`

**Try it with the sample data:**

    python -c "from app.data_processing import process_and_save; print(process_and_save('tests/sample_data/raw_sample.csv'))"

**Run the tests for this module:**

    python -m pytest tests/test_data_processing.py tests/test_categorise.py tests/test_process_and_save.py

**Limitations:**
- Only the languages listed in `CATEGORIES` get a group, and everything else becomes "Other".
- Duplicates are detected by repository name and collection date only.
- It uses Python's built-in `csv` module instead of pandas, so it works on computers that block pandas.