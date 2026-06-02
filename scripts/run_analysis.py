import argparse
import csv
import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from iris.data import load_data, load_data_csv
from iris.stats import format_stats
from iris.charts import save_chart, save_scatter
from iris.model import run_logistic_regression
from iris.report import build_report

DEFAULT_INPUT    = "data_derived/iris-samples-id-mapped-qc-filtered.csv"
ALL_SAMPLES_PATH = "data_derived/iris-all-samples.csv"
MAPPED_PATH      = "data_derived/iris-samples-id-mapped.csv"
QC_PATH          = "data_derived/iris-samples-id-mapped-qc-filtered.csv"

STATS_PATH       = "outputs/iris_stats.txt"
CHART_PATH       = "outputs/iris_means.png"
SCATTER_PATH     = "outputs/iris_scatter.png"
LR_REPORT_PATH   = "outputs/iris_logreg.txt"
LR_PLOT_PATH     = "outputs/iris_logreg.png"
LR_SCATTER_PATH  = "outputs/iris_scatterplot_withboundaries.png"
HTML_REPORT_PATH = "outputs/iris_report.html"


def count_csv_rows(path):
    with open(path, newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1  # subtract header


def collect_pipeline_counts():
    """Return sample counts at each pipeline stage, or None if files are unavailable."""
    try:
        return {
            "all_samples":      count_csv_rows(ALL_SAMPLES_PATH),
            "after_id_mapping": count_csv_rows(MAPPED_PATH),
            "after_qc_join":    count_csv_rows(QC_PATH),
        }
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Iris analysis pipeline.")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT,
                        help="Input CSV with headers and optional QC_CALL column "
                             "(only PASS rows are analysed).")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.suffix == ".csv":
        print(f"Loading {args.input} (CSV format, filtering to QC_CALL==PASS)")
        data = load_data_csv(args.input)
    else:
        data = load_data(args.input)

    md5 = hashlib.md5(input_path.read_bytes()).hexdigest()
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        git_commit = "unavailable"

    pipeline_counts = collect_pipeline_counts()
    if pipeline_counts is not None:
        n_used = sum(len(data[cls]["sepal_length"]) for cls in data)
        pipeline_counts["after_qc_pass"] = n_used

    output = format_stats(data)
    print(output)
    with open(STATS_PATH, "w") as f:
        f.write(output + "\n")
    print(f"\nResults written to {STATS_PATH}")

    save_chart(data, CHART_PATH)
    print(f"Chart written to {CHART_PATH}")

    save_scatter(data, SCATTER_PATH)
    print(f"Scatter written to {SCATTER_PATH}")

    lr_report = run_logistic_regression(data, LR_REPORT_PATH, LR_PLOT_PATH, LR_SCATTER_PATH)
    print(f"Logistic regression plot written to {LR_PLOT_PATH}")
    print(f"Logistic regression report written to {LR_REPORT_PATH}")

    html = build_report(data, lr_report, CHART_PATH, SCATTER_PATH, LR_PLOT_PATH, LR_SCATTER_PATH,
                        input_file=str(input_path), md5=md5,
                        timestamp=run_timestamp, git_commit=git_commit,
                        pipeline_counts=pipeline_counts)
    with open(HTML_REPORT_PATH, "w") as f:
        f.write(html)
    print(f"HTML report written to {HTML_REPORT_PATH}")
