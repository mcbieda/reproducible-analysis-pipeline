# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the script

```bash
python src/explore_iris.py
```

This runs all analysis in sequence: computes stats, saves charts, and trains/evaluates the logistic regression model. All outputs land in `outputs/`.

## Project structure

Single-script EDA and ML project on Fisher's Iris dataset.

- `data/iris.data` — 150 samples, CSV with no header: `sepal_length, sepal_width, petal_length, petal_width, class`
- `src/explore_iris.py` — all logic: data loading, hand-rolled stats (mean/median/sd), matplotlib charts, sklearn logistic regression
- `outputs/` — generated files (stats text, 4 PNG charts)

## Analyses and outputs

The script runs four analyses in order:

**1. Descriptive statistics** (`outputs/iris_stats.txt`)
Per-class summary of all four measurements (sepal/petal length and width). Stats are hand-rolled (no numpy/pandas): mean, median, and sample standard deviation (ddof=1). Results are printed to stdout and written to file.

**2. Mean ± SD bar chart** (`outputs/iris_means.png`)
Grouped bar chart with one bar per class per measurement. Error bars show ±1 SD. Useful for spotting which measurements best separate the three species.

**3. Petal scatter plot** (`outputs/iris_scatter.png`)
Petal length (x) vs. petal width (y), all 150 samples colored by class. Shows the natural clustering and the linear separability of setosa from the other two.

**4. Logistic regression** (`outputs/iris_logreg.txt`, `outputs/iris_logreg.png`, `outputs/iris_scatterplot_withboundaries.png`)
Multiclass logistic regression trained on petal length + petal width only (80/20 stratified split, `random_state=42`). Outputs: accuracy + confusion matrix to text file; decision boundary overlaid on test-set points; decision boundary overlaid on full dataset. Uses only petal dimensions so the boundary can be rendered in 2D.

## Documentation

`docs/README-methods.md` documents the theoretical basis for each statistical and ML method used. Update it whenever a method is changed or a new one is added.

## Architecture notes

`load_data()` returns a nested `defaultdict`: `data[class_name][column_name] -> list[float]`. All downstream functions (stats formatting, charting, logistic regression) consume this structure. The logistic regression uses only petal dimensions (not all 4 features) to produce interpretable 2D decision boundary plots.

## Dependencies

No requirements file. Imports in use: `matplotlib`, `numpy`, `sklearn`. Install with:

```bash
pip install matplotlib numpy scikit-learn
```
