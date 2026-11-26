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


## Snapshot Data Processing (Member 2: Shabana)

**File:** `app/data_processing.py`

This part cleans the technology snapshot files collected from GitHub, so the analysis and the dashboard can trust the numbers.

| Function | What it does |
|---|---|
| `load_snapshot(path)` | Opens a snapshot CSV, ignores a hidden character at the start, and rejects wrong file types, missing files, empty files and missing columns |
| `clean_snapshot(rows)` | Removes duplicates (same technology, repo and date), drops invalid or negative star counts, fills a missing language with `Unknown`, and adds a category |
| `categorise_domain(technology)` | Puts a technology into one of 9 domains: Web, AI, Mobile, Cybersecurity, Cloud, AR/VR, Blockchain, Data Science, IoT (anything else is `Other`) |
| `process_snapshot(raw_path)` | Runs the steps above and saves the result in `data/processed/` |

**Raw snapshot columns:** `collected_on, technology, full_name, language, stars, topics`

**Processed columns:** `collected_on, technology, repo_name, language, category, stars, topics` (`full_name` becomes `repo_name`, and `category` is the domain of the technology)

A repo that belongs to two technologies (for example next.js under react and nextjs) is kept as two rows, because the duplicate check includes the technology.

**Try it:**

    python -c "from app.data_processing import process_snapshot; print(process_snapshot('data/raw/YOUR_SNAPSHOT.csv'))"

**Run the tests:**

    python -m pytest tests/test_snapshot.py

**Limitations:**
- A technology that is not in `TECHNOLOGY_DOMAINS` becomes `Other` until someone adds it.
- Star counts written with a comma (for example `1,500`) are treated as invalid and the row is dropped.
- One snapshot only shows popularity on one day. Growth needs at least two snapshots from different days.
- Stars measure popularity, not quality, and unusual star counts need a manual check.