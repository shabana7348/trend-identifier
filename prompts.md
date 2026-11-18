# Prompt Log

Structured prompts used by the team, and how each AI output was verified.

## Member 2 (Shabana): Data Processing

### 1. Planning features
- **Prompt (summary):** I gave the AI our project requirements and the team's module split, and asked what `data_processing.py` should do and in what order to build it.
- **AI output:** four functions: `load_raw_data`, `clean_data`, `categorise_technology`, `process_and_save`, each with its own tests.
- **How I verified:** I compared the functions with the module description in our team plan. I counted the problems in my sample CSV by hand (one duplicate row, one negative-stars row), so I knew `clean_data` must turn 12 rows into 10, and wrote a test for that.

### 2. Explaining errors
- **pandas blocked:** I pasted the pytest error "DLL load failed ... An Application Control policy has blocked this file". The AI explained that my Windows security policy blocks the file, so it was not a bug in my code, and suggested Python's built-in `csv` module instead. **Verified:** I rewrote the module, confirmed line 1 said `import csv`, and ran pytest until all tests passed.
- **Merge conflict in `exceptions.py`:** I pasted the CONFLICT message and the file. The AI explained that both sides looked identical because one had a hidden character at the start of line 1. Its first cleanup command did not fully fix the file, so I printed the file again, saw the problem, and used a second command that rewrote it cleanly. **Verified:** no conflict markers, no hidden character, and pytest passed before I committed.
- **`ModuleNotFoundError: requests`** after merging Sadhika's work: the AI explained that my virtual environment was missing a new package. **Verified:** after `pip install -r requirements.txt`, all 15 tests passed.
- **"Connection was reset" on git commands:** the AI explained it was a network problem, not a Git problem. **Verified:** the same command worked after retrying.

### 3. Test ideas
- **Prompt (summary):** I asked for edge cases to test for `clean_data`, `categorise_technology` and `process_and_save`.
- **AI output:** duplicates, the same repo on different days, a missing language, negative stars, non-numeric stars, an empty list, capital letters and spaces in a language name, `None`, an unknown language, a missing output folder and a wrong file type.
- **How I verified:** I ran every test with pytest and checked the results against my real sample file.

### 4. How I check AI output
- I never kept AI code without running `python -m pytest`.
- When an instruction did not work (a paste that did not save, a fix that left a hidden character), I reported the exact error back instead of guessing.
- Every function went through a branch, a pull request and a teammate's approval before merging.