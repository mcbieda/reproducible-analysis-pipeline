"""
iris-modification.py — generates derived iris datasets.

Outputs (relative to repo root):
  data_derived/iris-original-add-ids.csv  — original data with headers and sampleID
  data_derived/iris-simulated-data.csv    — simulated samples based on per-class means
  data_derived/iris-all-samples.csv       — iris-original-add-ids + iris-simulated-data stacked
"""

import csv
import math
import os
import random

# Paths
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
OUT_DIR = os.path.join(REPO_ROOT, "data_derived")

IRIS_DATA = os.path.join(DATA_DIR, "iris.data")

BASICMOD_CSV = os.path.join(OUT_DIR, "iris-original-add-ids.csv")
SIMDATA_CSV = os.path.join(OUT_DIR, "iris-simulated-data.csv")
COMBINED_CSV = os.path.join(OUT_DIR, "iris-all-samples.csv")

COLUMNS = ["sampleID", "sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
FEATURES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

RANDOM_SEED = 42
SIM_SD = 0.2
SIM_SAMPLES_PER_CLASS = 4


def make_sample_id(lo, hi, used):
    """Return a unique sampleID with letter A-F and number in [lo, hi]."""
    while True:
        letter = random.choice("ABCDEF")
        number = random.randint(lo, hi)
        sid = f"{letter}-{number:04d}"
        if sid not in used:
            used.add(sid)
            return sid


def load_iris():
    """Return list of dicts with feature values (float) and class (str)."""
    rows = []
    with open(IRIS_DATA, newline="") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            rows.append({
                "sepal_length": float(parts[0]),
                "sepal_width":  float(parts[1]),
                "petal_length": float(parts[2]),
                "petal_width":  float(parts[3]),
                "class":        parts[4],
            })
    return rows


def write_basicmod(rows):
    used_ids = set()
    with open(BASICMOD_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["sampleID"] = make_sample_id(1, 8999, used_ids)
            writer.writerow({col: out[col] for col in COLUMNS})
    print(f"Wrote {BASICMOD_CSV}")


def class_means(rows):
    """Return {class_name: {feature: mean}}."""
    buckets = {}
    for row in rows:
        cls = row["class"]
        if cls not in buckets:
            buckets[cls] = {f: [] for f in FEATURES}
        for feat in FEATURES:
            buckets[cls][feat].append(row[feat])
    return {
        cls: {feat: sum(vals) / len(vals) for feat, vals in feats.items()}
        for cls, feats in buckets.items()
    }


def box_muller():
    """Return one standard-normal sample via Box-Muller."""
    while True:
        u1 = random.random()
        u2 = random.random()
        if u1 > 0:
            z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            return z


def write_simdata(means):
    used_ids = set()
    with open(SIMDATA_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for cls, feat_means in means.items():
            for _ in range(SIM_SAMPLES_PER_CLASS):
                row = {"class": cls, "sampleID": make_sample_id(9000, 9999, used_ids)}
                for feat, mean in feat_means.items():
                    value = mean + SIM_SD * box_muller()
                    row[feat] = max(0.0, round(value, 1))
                writer.writerow({col: row[col] for col in COLUMNS})
    print(f"Wrote {SIMDATA_CSV}")


def write_combined():
    with open(COMBINED_CSV, "w", newline="") as out_f:
        writer = None
        for src in (BASICMOD_CSV, SIMDATA_CSV):
            with open(src, newline="") as in_f:
                reader = csv.DictReader(in_f)
                if writer is None:
                    writer = csv.DictWriter(out_f, fieldnames=reader.fieldnames)
                    writer.writeheader()
                for row in reader:
                    writer.writerow(row)
    print(f"Wrote {COMBINED_CSV}")


def main():
    random.seed(RANDOM_SEED)
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = load_iris()
    write_basicmod(rows)
    means = class_means(rows)
    write_simdata(means)
    write_combined()


if __name__ == "__main__":
    main()
