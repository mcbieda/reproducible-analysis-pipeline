# Reproducible Analysis Pipeline

A major issue with agentic coding is trusting the results. Intermediate outputs allow one to inspect and verify steps along the way to the final outputs, as opposed to hoping that they are correct. Here I present a demonstration of reproducible scientific analysis pipelines built using agentic coding with [Claude Code](https://claude.ai/code). The project uses a modified Fisher's Iris dataset to illustrate a realistic multi-stage pipeline: ID mapping from one set of IDs to another, QC filtering, exploratory data analysis, and machine learning. Notably, there are IDs that don't map to the final IDs and also samples that fail QC and some that don't have QC information. There are some intermediate outputs that display these ids for investigation.

The focus is on two ideas: (1) making every pipeline stage an explicit, inspectable artifact rather than an in-memory transformation, and (2) exploring how agentic coding can support good data engineering practices when explicit specifications and reproducibility are treated as critical and necessary.

**This repo will be updated periodically to test approaches to code and output validation.**

---

## What This Demonstrates

Each stage of the pipeline is designed to illustrate a pattern common in scientific data analysis:

- **Explicit intermediate outputs** — every transformation writes a named file to `data_derived/`, making the pipeline auditable and each step independently inspectable
- **ID mapping with missing IDs** — samples flow through the pipeline under their original IDs until they are linked to a canonical identifier via an explicit merge, with diagnostics recording what matched and what didn't
- **QC filtering with provenance and missing QC values** — QC calls are applied as a join rather than an in-place filter, so the pre- and post-QC datasets both exist and the filtering decision is recorded
- **Reproducibility by construction** — fixed random seeds, explicit computation of statistics, and no in-memory state between stages

---

## Typical Pipeline Flow

In a standard analysis, an **ID mapping file** (linking sample IDs to canonical identifiers) and a **QC calls file** (recording pass/fail status per sample) would be supplied from upstream sources — a sample tracking system and a QC pipeline respectively. The analysis pipeline in `scripts/` is designed around this assumption.

```
data/iris-all-samples.csv (a modified iris data file)    │
    ▼
scripts/iris-merge-and-qc.py   ← receives iris-id-map.csv and iris-qc-calls.csv as inputs
    ├── data_derived/iris-samples-id-mapped.csv
    ├── outputs/iris-samples-id-mapped-summary.json        (id join diagnostics)
    ├── data_derived/iris-samples-id-mapped-qc-filtered.csv
    └── outputs/iris-samples-id-mapped-qc-filtered-summary.json (summary of qc filtering)
    │
    ▼
scripts/run_analysis.py
    ├── outputs/iris_stats.txt
    ├── outputs/iris_means.png
    ├── outputs/iris_scatter.png
    ├── outputs/iris_logreg.txt
    ├── outputs/iris_logreg.png
    ├── outputs/iris_scatterplot_withboundaries.png
    └── outputs/iris_report.html
```

---

## Generating Data for Demonstration

The `iris` dataset does not contain sampleIDs or column names, as given in typical files. Nor is there a need for any QC calls on the samples. To make this a more realistic and fully self-contained demonstration, `utilities/` contains scripts that generate the input files the pipeline would normally receive from upstream. These are not part of the analysis itself — they exist to produce realistic inputs. Altering these to add additional samples or samples with different characteristics is straightforward.

```
data/iris.data
    │
    ▼
utilities/iris-modification.py
    ├── data_derived/iris-original-add-ids.csv    (raw data + column names + sampleIDs)
    ├── data_derived/iris-simulated-data.csv       (simulated samples from class means)
    └── data_derived/iris-all-samples.csv          (combined; final input file of sample data)

utilities/iris-make-map-qc.py
    ├── data_derived/iris-id-map.csv               (sampleID → FINAL_ID mapping)
    └── data_derived/iris-qc-calls.csv             (FINAL_ID + PASS/FAIL QC calls)
```

`iris-make-map-qc.py` generates an ID mapping file and QC calls file with realistic characteristics — deliberate mismatches, extra IDs on both sides, and a realistic PASS/FAIL rate — so that the merge and QC filtering steps in `scripts/` behave as they would against real upstream inputs.

---

## Project Structure

```
├── data/                  Raw input data (never modified)
├── data_derived/          Intermediate pipeline outputs
├── outputs/               Final analysis outputs (charts, stats, reports, JSON summaries)
├── scripts/               Analysis pipeline
│   ├── iris-merge-and-qc.py    ID mapping + QC filtering
│   └── run_analysis.py         EDA and ML analysis
├── src/iris/              Importable Python package (loading, stats, charts, model, report)
├── utilities/             Standalone scripts for generating demonstration input files
└── docs/                  Methods documentation and pipeline specifications
```

---

## Running It

```bash
pip install -r requirements.txt

# Generate demonstration inputs (utilities — not part of the analysis)
python utilities/iris-modification.py
python utilities/iris-make-map-qc.py

# Run the analysis pipeline (scripts)
python scripts/iris-merge-and-qc.py
python scripts/run_analysis.py
```

All intermediate files land in `data_derived/`. Final outputs — charts, stats, HTML report, and JSON join summaries — land in `outputs/`. Note that the HTML report summarizes the data analysis, but not the ID mapping and filtering steps.

---

## Analysis Outputs

| File | Description |
|---|---|
| `iris_stats.txt` | Per-class mean, median, and SD for all four measurements |
| `iris_means.png` | Grouped bar chart of means ± 1 SD by class |
| `iris_scatter.png` | Petal length vs. width scatter plot colored by class |
| `iris_logreg.txt` | Logistic regression accuracy and confusion matrix |
| `iris_logreg.png` | Decision boundary on test-set points |
| `iris_scatterplot_withboundaries.png` | Decision boundary on full dataset |
| `iris_report.html` | Self-contained HTML report with provenance |
| `iris-samples-id-mapped-summary.json` | Join diagnostics: ID mapping merge |
| `iris-samples-id-mapped-qc-filtered-summary.json` | Join diagnostics: QC merge |

---

## Reproducibility

All random operations use a fixed seed of 42. Running the pipeline from scratch will reproduce all intermediate files and outputs exactly. Statistics are computed without numpy or pandas to keep the implementation transparent.

---

## Dependencies

- Python 3.8+
- `matplotlib`, `numpy`, `scikit-learn`
