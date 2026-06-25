# Reproducible Analysis Pipeline

## Overall Goal

**I'm using agentic coding for data analysis. How do I trust the results?**

This repository demonstrates a small but somewhat realistic scientific data analysis pipeline built with
agentic coding using [Claude Code](https://claude.ai/code). It uses a modified Fisher's Iris
dataset to illustrate a multi-stage workflow involving sample ID mapping, QC filtering,
exploratory analysis, statistical summaries, and machine learning.

This repository is the **reference implementation**. A companion repository,
[`reproducible-analysis-pipeline-reproduction-check-analysis`](https://github.com/mcbieda/reproducible-analysis-pipeline-reproduction-check-analysis),
independently reimplements the final analysis stage from the same specification and input data
to check whether the analytical results can be reproduced.

Of course, this is just **one** part of verifying results: for this small analysis, examining the code closely is easy; looking at whether results are reasonable is, of course, required; and some basic sanity checks like numbers of samples are pretty simple. But the idea of reimplementing is a very attractive option to (partially) validate results.

**Can a different implementation reproduce the same analytical results?**

Yes. The companion reproduction repository produces the same analytical results from a different
implementation. This provides a practical example of specification-driven validation: instead of
trusting that generated code is correct, we define expected behavior, regenerate the analysis
independently, and compare the outputs.

**What does this repository demonstrate?**

This repository demonstrates two related ideas:

1. **Reproducible pipeline design** — each pipeline stage writes explicit, inspectable artifacts
   rather than relying on hidden in-memory transformations.
2. **Validation of agentic coding outputs** — analysis code generated or developed with AI
   assistance still needs independent output-level checks.

The key point is simple: generating code is not enough. For scientific and analytical workflows,
the outputs need to be inspectable, reproducible, and independently checkable.

---

## Relationship to the Reproduction Repository

| | This repository | Companion reproduction repository |
|---|---|---|
| Role | Reference implementation | Independent reproduction check |
| Scope | Full demonstration pipeline | Final analysis stage only |
| Input | Raw iris data plus generated demonstration files | the modified data from this pipeline |
| Purpose | Build the pipeline and produce reference outputs | Verify that the analytical outputs can be reproduced |
| Code relationship | Original implementation | Reimplemented from specification, not copied |

This repository has a broader scope than the reproduction repository. It includes utilities that
create realistic demonstration inputs, including modified iris data, sample IDs, ID mappings, and
QC calls. The reproduction repository starts later in the workflow: it takes the final
QC-filtered input file and independently reproduces the final analysis outputs.

Together, the two repositories demonstrate a one key part in a validation process:

1. Build a reference analysis pipeline.
2. Write explicit specifications for the pipeline behavior.
3. Reimplement the analytically important stage from the specification.
4. Compare the reproduced outputs against the reference outputs.
5. Document exact matches and expected differences.

**Other steps would include: examining whether results are reasonable; doing basic sanity checks with the numbers/sample characteristics; examining the code.**

---

## Project Overview

The pipeline uses a modified version of the Fisher's Iris dataset to mimic features common in
real scientific analysis workflows:

- raw input data that must be prepared before analysis
- sample IDs that need to be mapped to final canonical IDs
- missing or unmatched IDs
- QC calls that determine which samples are retained
- intermediate files that allow each transformation to be inspected
- final statistical and machine learning outputs
- a self-contained HTML report with provenance metadata

The pipeline is intentionally small, but the structure reflects larger real-world workflows:
data preparation, ID mapping, QC merge, analysis, reporting, and validation.

---

## What This Demonstrates

Each stage of the pipeline illustrates a pattern common in scientific data analysis.

- **Explicit intermediate outputs**  
  Every transformation writes a named file to `data_derived/`, making the pipeline auditable and
  each step independently inspectable.

- **ID mapping with missing IDs**  
  Samples flow through the pipeline under their original IDs until they are linked to canonical
  identifiers through an explicit mapping step. Diagnostics record which IDs matched and which
  did not.

- **QC filtering with provenance**  
  QC calls are applied through a merge rather than an invisible in-memory filter. Both pre-QC and
  post-QC datasets are retained, and the filtering decision is recorded.

- **Reproducibility by construction**  
  Random seeds are fixed, outputs are written to disk, and the analysis does not depend on hidden
  notebook state.

- **Specification-driven validation**  
  The repository includes specifications detailed enough for the final analysis stage to be
  reimplemented independently and checked against the reference outputs.

---

## Typical Pipeline Flow

In a standard analysis, an **ID mapping file** and a **QC calls file** would often come from
upstream systems, such as a sample tracking system and a QC pipeline. This demonstration
generates those inputs locally so that the full workflow is self-contained.

```text
data_derived/iris-all-samples.csv
    │
    ▼
scripts/iris-merge-and-qc.py
    ├── data_derived/iris-samples-id-mapped.csv
    ├── outputs/iris-samples-id-mapped-summary.json
    ├── data_derived/iris-samples-id-mapped-qc-filtered.csv
    └── outputs/iris-samples-id-mapped-qc-filtered-summary.json
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

## Generating Demonstration Data

The original iris dataset does not contain sample IDs, canonical IDs, or QC calls. To make the
example more realistic, the `utilities/` directory contains scripts that generate the files a
pipeline like this might normally receive from upstream sources.

```text
data/iris.data
    │
    ▼
utilities/iris-modification.py
    ├── data_derived/iris-original-add-ids.csv
    ├── data_derived/iris-simulated-data.csv
    └── data_derived/iris-all-samples.csv

utilities/iris-make-map-qc.py
    ├── data_derived/iris-id-map.csv
    └── data_derived/iris-qc-calls.csv
```

`iris-modification.py` adds column names and sample IDs to the original iris data and creates
additional simulated samples.

`iris-make-map-qc.py` generates an ID mapping file and a QC calls file. These include realistic
edge cases such as deliberate mismatches, extra IDs, failed QC calls, and missing QC information.
Those edge cases allow the merge and QC stages to produce useful diagnostics rather than simply
passing every row through the pipeline.

The utility scripts are not the scientific analysis itself. They exist to create realistic,
self-contained demonstration inputs.

---

## Running the Pipeline

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate demonstration inputs:

```bash
python utilities/iris-modification.py
python utilities/iris-make-map-qc.py
```

Run the analysis pipeline:

```bash
python scripts/iris-merge-and-qc.py
python scripts/run_analysis.py
```

Intermediate files are written to `data_derived/`.

Final outputs, including charts, statistics, reports, and JSON summaries, are written to
`outputs/`.

---

## Analysis Outputs

| File | Description |
|---|---|
| `iris_stats.txt` | Per-class mean, median, and sample standard deviation for all four measurements |
| `iris_means.png` | Grouped bar chart of means ± 1 SD by class |
| `iris_scatter.png` | Petal length vs. petal width scatter plot colored by class |
| `iris_logreg.txt` | Logistic regression accuracy and confusion matrix |
| `iris_logreg.png` | Decision boundary plot on test-set points |
| `iris_scatterplot_withboundaries.png` | Decision boundary plot on the full dataset |
| `iris_report.html` | Self-contained HTML report with embedded images and provenance metadata |
| `iris-samples-id-mapped-summary.json` | ID mapping join diagnostics |
| `iris-samples-id-mapped-qc-filtered-summary.json` | QC merge and filtering diagnostics |

The HTML report includes provenance metadata and sample counts showing how many samples were
retained at each stage.

---

## Specifications

Each major script has a corresponding specification in `docs/`.

| Specification | Corresponding code |
|---|---|
| `docs/spec-iris-modification.md` | `utilities/iris-modification.py` |
| `docs/spec-iris-make-idmap-qc-files.md` | `utilities/iris-make-map-qc.py` |
| `docs/spec-iris-merge-and-qc.md` | `scripts/iris-merge-and-qc.py` |
| `docs/spec-iris-analysis-pipeline.md` | `scripts/run_analysis.py` and `src/iris/` |

The final analysis specification is also used by the companion reproduction repository to
independently recreate the analysis stage and compare the outputs against this reference
implementation.

---

## Reproducibility

All random operations use a fixed seed of `42`.

Running the pipeline from scratch should reproduce the same intermediate files and final outputs,
assuming the same dependency versions.

Descriptive statistics are computed explicitly rather than relying on NumPy or pandas summary
functions. This is intentional: the goal is to make the calculation logic transparent and easy to
inspect.

---

## Validation Pattern

This repository is part of a two-repository validation pattern.

The first repository — this one — builds the full reference pipeline and produces the expected
outputs.

The second repository independently reimplements the final analysis stage using the same
specification and the same QC-filtered input data. The reproduced results are then compared
against the reference outputs.

This is related to a “double programming” approach: two implementations are allowed to differ
internally, but they should converge on the same externally visible analytical results.


The important validation question is:

> Did an independent implementation reproduce the same analytical outputs? _(and it did)_

---

## Project Structure

```text
├── data/
│   └── Raw input data

├── data_derived/
│   └── Intermediate pipeline outputs

├── outputs/
│   └── Final analysis outputs, charts, reports, and JSON summaries

├── scripts/
│   ├── iris-merge-and-qc.py
│   └── run_analysis.py

├── src/iris/
│   └── Importable Python package for loading, statistics, charts, modeling, and reporting

├── utilities/
│   └── Standalone scripts for generating demonstration input files

└── docs/
    └── Methods documentation and pipeline specifications
```

---

## Dependencies

- Python 3.8+
- `matplotlib`
- `numpy`
- `scikit-learn`

See `requirements.txt` for pinned versions.

---

## Why This Matters

Agentic coding can quickly produce useful analysis code, but speed does not remove the need for
validation. In data analysis, correctness depends on the outputs, not just on whether the code
runs or looks reasonable.

This repository demonstrates a practical approach:

1. make each pipeline stage explicit
2. write inspectable intermediate outputs
3. document the intended behavior in specifications
4. produce reference outputs
5. independently reproduce the analytically important stage
6. compare the reproduced outputs against the reference results

The broader lesson is that AI-assisted analysis pipelines should be designed for verification
from the beginning.
