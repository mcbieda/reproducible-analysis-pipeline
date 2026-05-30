import argparse
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

DATA_PATH       = "data/iris.data"
STATS_PATH      = "outputs/iris_stats.txt"
CHART_PATH      = "outputs/iris_means.png"
SCATTER_PATH    = "outputs/iris_scatter.png"
LR_REPORT_PATH  = "outputs/iris_logreg.txt"
LR_PLOT_PATH    = "outputs/iris_logreg.png"
LR_SCATTER_PATH = "outputs/iris_scatterplot_withboundaries.png"
HTML_REPORT_PATH = "outputs/iris_report.html"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Iris analysis pipeline.")
    parser.add_argument("input", nargs="?", default=DATA_PATH,
                        help="Input file. Use the default iris.data format, or a CSV with headers "
                             "and QC_CALL column (only PASS rows are analysed).")
    args = parser.parse_args()

    if args.input != DATA_PATH:
        print(f"Loading {args.input} (CSV format, filtering to QC_CALL==PASS)")
        data = load_data_csv(args.input)
    else:
        data = load_data(DATA_PATH)

    input_path = Path(args.input)
    md5 = hashlib.md5(input_path.read_bytes()).hexdigest()
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        git_commit = "unavailable"

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
                        timestamp=run_timestamp, git_commit=git_commit)
    with open(HTML_REPORT_PATH, "w") as f:
        f.write(html)
    print(f"HTML report written to {HTML_REPORT_PATH}")
