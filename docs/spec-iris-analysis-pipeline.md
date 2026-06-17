# spec-iris-analysis-pipeline.md - a specification document for the iris analysis pipeline

# GOAL
Create a Python analysis pipeline that loads a QC-filtered iris dataset, computes descriptive
statistics, produces exploratory charts, trains a logistic regression model, and generates a
self-contained HTML report with provenance information and pipeline sample counts.

# STRUCTURE
The pipeline consists of an importable package and an orchestration script:

 - `src/iris/` — Python package with five modules: data.py, stats.py, charts.py, model.py, report.py
 - `scripts/run_analysis.py` — entry point; wires the modules together and defines all output paths

The modules in `src/iris/` do not import each other except that `stats.py` and `charts.py` import
`COLUMNS` from `data.py`. All other wiring is done in `scripts/run_analysis.py`.

# RANDOM SEED
 - use a fixed random seed of 42 for all random operations (train/test split)

# DATA

 - default input file: `data_derived/iris-samples-id-mapped-qc-filtered.csv`
 - do NOT modify any files in data/ or data_derived/

# DEPENDENCIES
 - matplotlib, numpy, scikit-learn
 - statistics (mean, median, SD) must be computed without numpy or pandas — hand-rolled only

# OUTPUTS
 - all outputs go to the `outputs/` directory
 - `outputs/iris_stats.txt`
 - `outputs/iris_means.png`
 - `outputs/iris_scatter.png`
 - `outputs/iris_logreg.txt`
 - `outputs/iris_logreg.png`
 - `outputs/iris_scatterplot_withboundaries.png`
 - `outputs/iris_report.html`

---

# MODULE: src/iris/data.py

## Constants
 - `COLUMNS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]`

## Functions

### load_data(path)
 - loads the raw iris.data format: no header, comma-separated, 5 columns (4 floats + class string)
 - skips any rows that do not have exactly 5 fields
 - returns a nested defaultdict: `data[class_name][column_name] -> list[float]`

### load_data_csv(path)
 - loads a CSV file with a header row
 - if a `QC_CALL` column is present, only retain rows where QC_CALL == "PASS"
 - reads the class from the `class` column and feature values from COLUMNS
 - returns the same nested defaultdict structure as load_data()

---

# MODULE: src/iris/stats.py

## Functions — all hand-rolled, no numpy or pandas

### mean(xs)
 - arithmetic mean of a list of floats

### median(xs)
 - sort the list; return the middle value if odd length, or the average of the two middle values if even

### sd(xs)
 - sample standard deviation (ddof=1): sqrt( sum((x - mean)^2) / (n - 1) )

### format_stats(data)
 - produces a formatted text summary of all classes and all four measurements
 - for each class (sorted alphabetically), print a block with:
   - a header line of "=" characters and the class name
   - a column header row: variable, mean, median, sd
   - one row per measurement in COLUMNS order, values formatted to 4 decimal places
 - returns the full output as a string (also printed to stdout by the caller)

---

# MODULE: src/iris/charts.py

## Color scheme (Okabe-Ito colorblind-safe)
 - Iris-setosa:     #0072B2 (blue),  marker: circle ("o")
 - Iris-versicolor: #E69F00 (amber), marker: square ("s")
 - Iris-virginica:  #CC79A7 (mauve), marker: triangle-up ("^")

## Functions

### save_chart(data, path)
 - grouped bar chart: one group per measurement (x-axis), one bar per class per group
 - error bars show ±1 SD
 - x-axis tick labels: measurement names with underscores replaced by newlines
 - y-axis label: "cm"
 - title: "Iris: mean ± SD by measurement and class"
 - bar width: 0.25; bars centered on each x position with equal spacing between classes
 - no top or right spines
 - figsize=(10, 6), dpi=150
 - saves to path and closes the figure

### save_scatter(data, path)
 - scatter plot: petal_length (x-axis) vs petal_width (y-axis), all samples
 - one series per class using the color/marker scheme above
 - point size: 60, alpha: 0.75, white edge color, edge linewidth: 0.4
 - x-axis label: "Petal length (cm)"
 - y-axis label: "Petal width (cm)"
 - title: "Iris: petal width vs petal length"
 - no top or right spines
 - figsize=(8, 6), dpi=150
 - saves to path and closes the figure

---

# MODULE: src/iris/model.py

## Function: run_logistic_regression(data, report_path, plot_path, scatter_path)

### Data preparation
 - use only petal_length and petal_width as features (2D)
 - classes sorted alphabetically; build X (n_samples x 2) and y (n_samples,) arrays

### Train/test split
 - 80/20 stratified split, random_state=42

### Model
 - sklearn LogisticRegression, max_iter=200
 - fit on training set

### Text report (report_path)
 - write to report_path and return the report string
 - content:
   - header: "Logistic Regression — petal length + petal width"
   - separator line of "=" characters
   - train size and test size
   - accuracy on test set (4 decimal places): "Accuracy (test set):        X.XXXX"
   - accuracy on full dataset (4 decimal places): "Accuracy (full dataset):    X.XXXX"
   - confusion matrix with class names as column headers and row labels
     (use only the species part of the class name, e.g. "setosa" not "Iris-setosa")

### Decision boundary
 - compute a meshgrid over petal_length and petal_width ranges (padded by 0.3 on each side)
 - meshgrid resolution: 400 x 400
 - background region colors (light versions of the class colors):
   - setosa:     #b3d4e8
   - versicolor: #f5e0b3
   - virginica:  #ecd4e3
 - decision boundary lines: grey dashed, linewidth 0.8

### Plot 1 — test set (plot_path)
 - overlay decision boundary background and boundary lines
 - scatter only the test-set points using the class color/marker scheme
 - point size: 70, alpha: 0.9, white edge color, edge linewidth: 0.5
 - title: "Logistic regression decision boundary (test set, acc=X.XX)"
 - x/y labels: "Petal length (cm)", "Petal width (cm)"
 - no top or right spines; figsize=(8, 6), dpi=150

### Plot 2 — full dataset (scatter_path)
 - same decision boundary background and lines
 - scatter all samples (not just test set)
 - point size: 60, alpha: 0.75, white edge color, edge linewidth: 0.4
 - title: "Logistic regression decision boundary (all data, acc=X.XX)"
 - same axis labels and style as plot 1

---

# MODULE: src/iris/report.py

## Function: build_report(data, lr_report_text, chart_path, scatter_path, lr_plot_path,
##                        lr_scatter_path, input_file="", md5="", timestamp="",
##                        git_commit="", pipeline_counts=None)
 - returns a complete self-contained HTML string
 - all images are embedded as base64-encoded PNG data URIs (no external files)

## HTML structure and content

### Title
 - page title and h1: "Modified Iris Dataset Analysis"

### Intro paragraph
 - describe that this uses a synthetic dataset partially derived from Fisher's Iris dataset
 - mention: sample IDs added, simulated samples generated, ID mapping step, QC filtering step
 - note that these steps reflect a typical scientific analysis pipeline

### Provenance table
 - four rows: Input file, MD5, Run date/time, Git commit

### Pipeline sample counts section (if pipeline_counts is not None)
 - h2: "Pipeline Sample Counts"
 - table with columns: Stage, File, Samples
 - four rows:
   - "Starting samples"       | iris-all-samples.csv                             | pipeline_counts["all_samples"]
   - "After ID mapping"       | iris-samples-id-mapped.csv                       | pipeline_counts["after_id_mapping"]
   - "After QC join"          | iris-samples-id-mapped-qc-filtered.csv           | pipeline_counts["after_qc_join"]
   - "After QC PASS filter"   | (used in analysis)                               | pipeline_counts["after_qc_pass"]

### Analysis dataset summary paragraph
 - state the number of samples and number of classes used in the analysis

### Descriptive statistics section
 - h2: "Descriptive Statistics"
 - table: rows are class × variable combinations; columns are Class, Variable, mean, median, sd
 - values formatted to 4 decimal places

### Mean ± SD bar chart section
 - h2: "Mean ± SD by Measurement and Class"
 - embedded chart image
 - caption: "Error bars show ±1 SD. Petal dimensions show the clearest separation between species."

### Scatter plot section
 - h2: "Petal Length vs Petal Width"
 - embedded scatter image
 - caption noting the number of samples and separability of setosa

### Logistic regression section
 - h2: "Logistic Regression Model"
 - description of the model setup (petal length + width, 80/20 stratified split, random_state=42)
 - test-set accuracy and full-dataset accuracy (bold)
 - confusion matrix table

### Decision boundary plots
 - h2: "Decision Boundary — Test Set" with embedded plot and caption
 - h2: "Decision Boundary — All Data" with embedded plot and caption

---

# SCRIPT: scripts/run_analysis.py

## Inputs
 - default input: `data_derived/iris-samples-id-mapped-qc-filtered.csv`
 - accepts an optional command-line positional argument to override the input path
 - if the input file has a .csv extension, use load_data_csv(); otherwise use load_data()

## Pipeline counts
 - before running the analysis, attempt to read row counts from these three files:
   - `data_derived/iris-all-samples.csv`
   - `data_derived/iris-samples-id-mapped.csv`
   - `data_derived/iris-samples-id-mapped-qc-filtered.csv`
 - if any file is missing, set pipeline_counts to None
 - after loading data, add "after_qc_pass" to pipeline_counts: the total number of samples
   in the loaded dataset (sum of all per-class sample counts)

## Provenance
 - compute MD5 hash of the input file
 - record the current date/time as a string: "YYYY-MM-DD HH:MM:SS"
 - capture the current git commit hash via subprocess ("git rev-parse HEAD");
   if unavailable, use "unavailable"

## Execution order
 1. load data
 2. collect pipeline counts
 3. compute and write descriptive stats to outputs/iris_stats.txt (also print to stdout)
 4. save bar chart to outputs/iris_means.png
 5. save scatter plot to outputs/iris_scatter.png
 6. run logistic regression; write text report to outputs/iris_logreg.txt;
    save decision boundary plots to outputs/iris_logreg.png and
    outputs/iris_scatterplot_withboundaries.png
 7. build and write HTML report to outputs/iris_report.html
