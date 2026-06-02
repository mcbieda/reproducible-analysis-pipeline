import base64

from iris.data import COLUMNS
from iris.stats import mean, median, sd

CSS = """
body { font-family: Georgia, serif; background: #fff; color: #222; margin: 0; padding: 2rem; }
.wrap { max-width: 900px; margin: 0 auto; }
h1 { font-size: 1.8rem; border-bottom: 2px solid #333; padding-bottom: .4rem; }
h2 { font-size: 1.25rem; margin-top: 2.5rem; color: #333; }
p.caption { color: #555; font-size: .9rem; margin-top: .3rem; }
img { width: 100%; display: block; margin: 1rem 0; border: 1px solid #ddd; }
table { border-collapse: collapse; width: 100%; font-size: .9rem; margin: 1rem 0; }
th { background: #333; color: #fff; padding: .45rem .7rem; text-align: left; }
td { padding: .4rem .7rem; border-bottom: 1px solid #ddd; }
tr:nth-child(even) td { background: #f7f7f7; }
.acc { font-size: 1.1rem; margin: .5rem 0 1rem; }
table.provenance { width: auto; margin: .8rem 0 1.5rem; font-size: .9rem; }
table.provenance th { background: #555; padding: .35rem .8rem; white-space: nowrap; }
table.provenance td { padding: .35rem .8rem; font-family: monospace; }
table.provenance code { font-size: .85rem; }
"""

STAT_LABELS = ["mean", "median", "sd"]
STAT_FNS    = [mean, median, sd]


def _img(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<img src="data:image/png;base64,{b64}">'


def _stats_table(data):
    classes = sorted(data.keys())
    rows = ["<table>", "<tr><th>Class</th><th>Variable</th>"
            + "".join(f"<th>{s}</th>" for s in STAT_LABELS) + "</tr>"]
    for cls in classes:
        first = True
        for col in COLUMNS:
            xs = data[cls][col]
            cls_cell = f'<td rowspan="{len(COLUMNS)}">{cls}</td>' if first else ""
            first = False
            vals = "".join(f"<td>{fn(xs):.4f}</td>" for fn in STAT_FNS)
            rows.append(f"<tr>{cls_cell}<td>{col}</td>{vals}</tr>")
    rows.append("</table>")
    return "\n".join(rows)


def _lr_section(lr_report_text):
    lines = lr_report_text.strip().splitlines()

    acc_line = next((l for l in lines if "Accuracy (test set):" in l), "")
    acc = acc_line.split()[-1] if acc_line else "n/a"

    acc_full_line = next((l for l in lines if "Accuracy (full dataset):" in l), "")
    acc_full = acc_full_line.split()[-1] if acc_full_line else "n/a"

    train_line = next((l for l in lines if l.startswith("Train size:")), "")

    # Find confusion matrix: header row is the line after "Confusion matrix"
    cm_idx = next((i for i, l in enumerate(lines) if "Confusion matrix" in l), None)
    cm_html = ""
    if cm_idx is not None:
        header_parts = lines[cm_idx + 1].split()
        cm_rows = ["<table>",
                   "<tr><th></th>" + "".join(f"<th>{h}</th>" for h in header_parts) + "</tr>"]
        for row_line in lines[cm_idx + 2:]:
            parts = row_line.split()
            if not parts:
                break
            label = parts[0]
            vals = "".join(f"<td>{v}</td>" for v in parts[1:])
            cm_rows.append(f"<tr><th>{label}</th>{vals}</tr>")
        cm_rows.append("</table>")
        cm_html = "\n".join(cm_rows)

    return acc, acc_full, train_line.strip(), cm_html


def _pipeline_counts_section(counts):
    if not counts:
        return ""
    rows = [
        ("Starting samples", "iris-all-samples.csv",                        counts.get("all_samples", "—")),
        ("After ID mapping", "iris-samples-id-mapped.csv",                  counts.get("after_id_mapping", "—")),
        ("After QC join",    "iris-samples-id-mapped-qc-filtered.csv",      counts.get("after_qc_join", "—")),
        ("After QC PASS filter", "(used in analysis)",                      counts.get("after_qc_pass", "—")),
    ]
    trs = "".join(
        f"<tr><td>{stage}</td><td><code>{f}</code></td><td style='text-align:right'>{n}</td></tr>"
        for stage, f, n in rows
    )
    return f"""<h2>Pipeline Sample Counts</h2>
<table>
<tr><th>Stage</th><th>File</th><th>Samples</th></tr>
{trs}
</table>"""


def build_report(data, lr_report_text, chart_path, scatter_path, lr_plot_path, lr_scatter_path,
                 input_file="", md5="", timestamp="", git_commit="", pipeline_counts=None):
    acc, acc_full, train_info, cm_html = _lr_section(lr_report_text)
    n_samples = sum(len(data[cls]["sepal_length"]) for cls in data)
    n_classes = len(data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Modified Iris Dataset Analysis</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<h1>Modified Iris Dataset Analysis</h1>
<p>This analysis uses a synthetic dataset partially derived from Fisher's Iris dataset.
Sample IDs were added to the original measurements and additional simulated samples were generated
from per-class means. The dataset then passed through an ID mapping step — linking sample IDs to
canonical identifiers — and a QC filtering step, retaining only samples with a PASS call.
These steps reflect the structure of a typical scientific analysis pipeline in which sample
tracking and quality control are applied before downstream analysis.</p>
<table class="provenance">
  <tr><th>Input file</th><td>{input_file}</td></tr>
  <tr><th>MD5</th><td><code>{md5}</code></td></tr>
  <tr><th>Run date/time</th><td>{timestamp}</td></tr>
  <tr><th>Git commit</th><td><code>{git_commit}</code></td></tr>
</table>
{_pipeline_counts_section(pipeline_counts)}
<p>Analysis dataset — {n_samples} samples across {n_classes} species
(<em>setosa</em>, <em>versicolor</em>, <em>virginica</em>),
four measurements each (sepal/petal length and width).</p>

<h2>Descriptive Statistics</h2>
<p>Per-class mean, median, and sample standard deviation (ddof=1) for all four measurements.</p>
{_stats_table(data)}

<h2>Mean ± SD by Measurement and Class</h2>
{_img(chart_path)}
<p class="caption">Error bars show ±1 SD. Petal dimensions show the clearest separation between species.</p>

<h2>Petal Length vs Petal Width</h2>
{_img(scatter_path)}
<p class="caption">All {n_samples} samples. Setosa is linearly separable; versicolor and virginica overlap slightly.</p>

<h2>Logistic Regression Model</h2>
<p>Multiclass softmax logistic regression trained on petal length and petal width only
(80/20 stratified split, random_state=42). Using petal dimensions allows a 2D decision boundary plot.</p>
<p class="acc"><strong>Test-set accuracy: {acc}</strong> &nbsp;·&nbsp; <strong>Full-dataset accuracy: {acc_full}</strong> &nbsp;·&nbsp; {train_info}</p>
<p>Confusion matrix (rows = actual, columns = predicted):</p>
{cm_html}

<h2>Decision Boundary — Test Set</h2>
{_img(lr_plot_path)}
<p class="caption">Shaded regions show model decision areas. Points are held-out test samples.</p>

<h2>Decision Boundary — All Data</h2>
{_img(lr_scatter_path)}
<p class="caption">Same decision boundary overlaid on all {n_samples} samples.</p>

</div>
</body>
</html>"""
    return html
