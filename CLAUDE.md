# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the script

```bash
python scripts/run_analysis.py
```

This runs all analysis in sequence: computes stats, saves charts, and trains/evaluates the logistic regression model. All outputs land in `outputs/`.

## Project structure

EDA and ML project on Fisher's Iris dataset, split into a reusable package and an orchestration script.

- `data/iris.data` — 150 samples, CSV with no header: `sepal_length, sepal_width, petal_length, petal_width, class`
- `data_derived/` — intermediate pipeline outputs (staged CSV files produced by utilities and scripts)
- `src/iris/` — importable Python package: `data.py` (loading), `stats.py` (descriptive stats), `charts.py` (matplotlib), `model.py` (logistic regression), `report.py` (HTML report builder)
- `scripts/run_analysis.py` — EDA and ML entry point; defines all output paths and calls into `src/iris/`
- `scripts/iris-merge-and-qc.py` — merges `iris-all-samples.csv` with `iris-id-map.csv` and `iris-qc-calls.csv` via inner joins; writes filtered CSV outputs and JSON join diagnostics to `outputs/`
- `utilities/iris-modification.py` — generates `iris-original-add-ids.csv`, `iris-simulated-data.csv`, and `iris-all-samples.csv` in `data_derived/`
- `utilities/iris-make-map-qc.py` — generates demonstration ID mapping and QC fixture files (`iris-id-map.csv`, `iris-qc-calls.csv`) in `data_derived/`; not part of the analysis pipeline
- `outputs/` — final analysis outputs (stats text, PNG charts, HTML report, JSON join summaries)

## Analyses and outputs

The script runs four analyses in order:

**1. Descriptive statistics** (`outputs/iris_stats.txt`)
Per-class summary of all four measurements (sepal/petal length and width). Stats are hand-rolled (no numpy/pandas): mean, median, and sample standard deviation (ddof=1). Results are printed to stdout and written to file.

**2. Mean ± SD bar chart** (`outputs/iris_means.png`)
Grouped bar chart with one bar per class per measurement. Error bars show ±1 SD. Useful for spotting which measurements best separate the three species.

**3. Petal scatter plot** (`outputs/iris_scatter.png`)
Petal length (x) vs. petal width (y), all 150 samples colored by class. Shows the natural clustering and the linear separability of setosa from the other two.

**4. Logistic regression** (`outputs/iris_logreg.txt`, `outputs/iris_logreg.png`, `outputs/iris_scatterplot_withboundaries.png`, `outputs/iris_report.html`)
Multiclass logistic regression trained on petal length + petal width only (80/20 stratified split, `random_state=42`). Outputs: accuracy + confusion matrix to text file; decision boundary overlaid on test-set points; decision boundary overlaid on full dataset. Uses only petal dimensions so the boundary can be rendered in 2D.

## Documentation

`docs/README-methods.md` documents the theoretical basis for each statistical and ML method used. Update it whenever a method is changed or a new one is added.

Specification documents for the utility scripts live in `docs/`:
- `docs/spec-iris-modification.md` — spec for `utilities/iris-modification.py`
- `docs/spec-iris-make-idmap-qc-files.md` — spec for `utilities/iris-make-map-qc.py`
- `docs/spec-iris-merge-and-qc.md` — spec for `scripts/iris-merge-and-qc.py`
- `docs/spec-iris-analysis-pipeline.md` — spec for `scripts/run_analysis.py` and `src/iris/`

## Architecture notes

`load_data()` returns a nested `defaultdict`: `data[class_name][column_name] -> list[float]`. All downstream functions (stats formatting, charting, logistic regression) consume this structure. The `src/iris/` modules do not import each other except `stats.py` and `charts.py` importing from `data.py` for `COLUMNS` — all wiring is in `scripts/run_analysis.py`. The logistic regression uses only petal dimensions (not all 4 features) to produce interpretable 2D decision boundary plots.

## Dependencies

```bash
pip install -r requirements.txt
```
