# On linguistic and geographic distances in the Bandiagara

This repository reproduces the analyses and figures used in the paper entitled "On linguistic and geographic distances in the Bandiagara".

## Overview

The workflow is organized in four stages:

1. Prepare and shorten the lexical dataset.
2. Compute cognate clusters and a linguistic distance matrix.
3. Generate the illustrations and maps.
4. Run the statistical analyses.

All scripts should be run from the repository root.

## Requirements

Use the project Python environment (the repository is configured to use `myenv`).

On Windows PowerShell, the typical setup is:

```powershell
# from the project root
.
\myenv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If your environment is already activated, you can skip the activation step.

## Reproduction workflow

Run the scripts in the following order:

```powershell
python coverage.py
python distance.py
python get_illustrations.py
python get_statistics.py
```

### What each step does

- `coverage.py`
  - Loads the cleaned lexical dataset.
  - Selects a reduced set of languages and concepts.
  - Writes the shortened wordlist to `processed_data/value_cleaned_data-shortened.tsv`.

- `distance.py`
  - Cleans the shortened dataset.
  - Runs cognate clustering with LingPy.
  - Produces an aligned wordlist and saves the linguistic distance matrix to `matrices/linguistic_distance_matrix.csv`.

- `get_illustrations.py`
  - Generates the figures and maps used in the paper.
  - Outputs are written to the `Illustrations/` directory.

- `get_statistics.py`
  - Computes the statistical analyses reported in the study.
  - Results are printed to the console.

## Expected outputs

After the full workflow, you should have:

- `processed_data/value_cleaned_data-shortened.tsv`
- `processed_data/value_cleaned_data-clean.tsv`
- `processed_data/value_cleaned_data-clean-aligned.tsv`
- `matrices/linguistic_distance_matrix.csv`
- Figures and HTML maps in `Illustrations/`

## Data sources

Linguistic data:

Abbie Hantgan-Sonko, Promise Dodzi Kpoglu, Idrissa Amadiougo Sagara (June 1, 2026). Building a Consolidated Dogon Lexical Dataset. *The Small Bang*. Retrieved July 30, 2026 from https://bang.hypotheses.org/257

Geographic data:

Moran, Steven & Forkel, Robert & Heath, Jeffrey (eds.) 2016. *Dogon and Bangime Linguistics*. Jena: Max Planck Institute for the Science of Human History. Available online at http://dogonlanguages.info, accessed on 2026-07-30.

## Notes

- The repository already contains the required input files under `processed_data/` and `matrices/`.
- Run all commands from the project root so that the scripts can find the expected files.
- If you encounter dependency issues, ensure that your active Python environment matches the one used for the project.
