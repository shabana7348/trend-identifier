# trend-identifier
Emerging Technology and Trends Identifier
## Live technology snapshots

The dashboard reads real repository data from dated GitHub topic snapshots in `data/raw`.
Collect a snapshot from the project folder with:

    python -m app.data_collection

This searches the topics in `app/topics.py` and saves `data/raw/snapshot_YYYY-MM-DD.csv`.
Run it again on a later date to add a second snapshot and enable growth trends. The
unauthenticated collector waits between searches to respect GitHub's search API limit.
Set `GITHUB_TOKEN` to a GitHub token in your environment to use the higher authenticated
rate limit.

The separate language collector (`collect_data`) writes language data and is used by the
language analysis; it does not supply technology snapshots to the home dashboard.

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
